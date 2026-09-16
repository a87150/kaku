# Django 4.2 → 5.2 LTS 升级可行性评估

> 结论：**项目代码已具备 5.2 条件，但依赖链存在一个无法靠"升级版本"解决的硬阻塞，
> 因此本次决定暂缓**。本文记录完整证据、阻塞清单、后续执行路线，以及当前采取的补偿措施。

## 一、为什么要评估这一项

`docs/dependabot-audit.md` 里剩余的 7 条告警**全部是 Django**，且修复版本只存在于
5.2.x / 6.0.x 线 —— Django 4.2 已 EOL，不会再收到这些修复。也就是说：
**不跨大版本，这 7 条告警就一条也清不掉。**

## 二、验证方法（全程未污染现有环境）

不直接在项目 venv 里换 Django，而是把 5.2 的 wheel 旁挂出来，用 `PYTHONPATH` 让它遮蔽
venv 里的 4.2.30。探针跑完后删除临时目录即可，**venv 与 `requirements.txt` 全程未改动**。

旁挂工具已沉淀为 `scripts/probe_django.py`（只依赖标准库，后续再评估更替版本时可直接复用）。

```powershell
# 1) 从 PyPI 取 Django 5.2 wheel 并解包（pip 在沙箱下写不了临时目录，改用 urllib+zipfile）
.\venv\Scripts\python.exe scripts\probe_django.py 5.2.17

# 2) 让 5.2 优先于 venv 里的 4.2
$env:PYTHONPATH="C:\Users\a8715\Desktop\code\py\kaku\.tmp_dj52"
.\venv\Scripts\python.exe -c "import django; print(django.__version__, django.__file__)"

# 3) 跑基线
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test --verbosity 1
```

## 三、探针结果

### 3.1 第一个也是唯一一个代码级阻塞

```
File "venv\Lib\site-packages\notifications\base\models.py", line 148, in AbstractNotification
    class Meta:
TypeError: 'class Meta' got invalid attribute(s): index_together
```

`django-notifications-hq 1.8.3` 的 `AbstractNotification.Meta` 用了 `index_together`，
而该选项在 **Django 5.1 被移除**。

### 3.2 把这一行改成 `Meta.indexes` 之后

用影子包（把 `notifications` 复制一份到 `.tmp_probe/` 并改那一行）复跑：

| 项目 | 结果 |
|------|------|
| `manage.py check` | `System check identified no issues (0 silenced).` |
| `manage.py test` | `Ran 83 tests ... OK`（68.7s；4.2 下为 43.2s） |

**结论：项目自身代码在 Django 5.2 下没有其它代码级阻塞。**
allauth 65、crispy-forms 1.14、activity-stream 2.0.0、imagekit、captcha 的调用路径
以及 Redis 降级分支，全部原样通过。

### 3.3 附带确认：`kaku/compat_py314.py` 在 5.2 上会失效（好事）

| 版本 | `django/template/context.py` 的 `BaseContext.__copy__` |
|------|--------------------------------------------------------|
| 4.2.30（现用） | `duplicate = copy(super())` ← Python 3.13+ 会崩，必须打补丁 |
| 5.2.17 | `duplicate.__class__ = self.__class__` ← **上游已修** |

补丁本身有 `if "copy(super())" not in source: return` 的自检，升级后会自动空转，
届时可以连同 settings 顶部的调用一起删掉。

### 3.4 官方 Python 支持矩阵（PyPI 分类器实测）

| 版本 | `requires_python` | 声明支持 |
|------|-------------------|----------|
| 4.2.30（现用） | `>=3.8` | 3.8 – 3.12 |
| **5.2.17** | `>=3.10` | 3.10 – **3.14** |
| 6.0.8 | `>=3.12` | 3.12 – 3.14 |

即：本机 Python 3.14.7 目前跑在"官方不支持"的 4.2 上（靠 `compat_py314.py` 兜底）；
**升到 5.2 反而回到官方支持范围**——这是 5.2 除安全之外的第二个收益。

## 四、依赖阻塞清单（PyPI 实测数据）

| 包 | 当前 | 最新 | 上游声明的 Django 支持 | 判定 |
|----|------|------|------------------------|------|
| **django-notifications-hq** | 1.8.3 | 1.8.3（已停更） | 仅 3.2 / 4.0 / 4.1 | 🔴 **硬阻塞**：用 `index_together`，上游无新版本，只能自己 fork |
| django-crispy-forms | 1.14.0 | 2.7 | 2.7 要求 `django>=5.2` | 🟡 探针中 1.14 在 5.2 下未报错，但它是 2021 年的版本；且 2.x 把 `bootstrap4` 模板包拆成了独立的 `crispy-bootstrap4`，长期要迁移 |
| django-activity-stream | 2.0.0 | 2.0.0 | `Django>=3.2`，无 Django 分类器 | 🟡 探针通过；上游 2.0.0 是 2023 年版本，活跃度低 |
| django-redis | 5.2.0 | 7.0.0 | 7.0 要求 `Django>=5.2` | 🟡 5.2.0 只声明到 Django 4.0；探针通过（测试走降级路径），生产开了 Redis 需实测 |
| django-allauth | 65.19.2 | 65.19.3 | 4.2 – 6.1 | 🟢 兼容 |
| django-model-utils | 5.0.0 | 5.0.0 | 3.2 – 5.1 | 🟢 兼容 |
| django-simple-captcha | 0.7.0 | 0.7.0 | `Django>=4.2` | 🟢 兼容 |
| django-imagekit | 6.1.0 | 6.1.1 | — | 🟢 兼容 |
| mistune / bleach / Pillow / requests / sqlparse / setuptools | — | 已是最新 | — | 🟢 |

**一句话**：Django 本身能升，卡住的是 `django-notifications-hq` 这个已经没人维护的包。
用它换来的 7 条告警清除，代价是要把它的源码内联进项目自己维护。

## 五、若日后推进：执行路线

1. **先处置 notifications（唯一真正的前置决策）**，三选一：
   - **a. 内联 fork（推荐）**：把 `site-packages/notifications/` 复制为项目内顶层包
     `notifications/`，**保持 `app_label = 'notifications'` 与迁移目录原样**（表名、
     迁移图都不变，不需要数据迁移），只把 `index_together` 改成
     `indexes = [models.Index(fields=['recipient', 'unread'])]` 并补一条迁移；
     `requirements.txt` 去掉 `django-notifications-hq`（注意 `jsonfield` 可能仍被需要）。
   - **b. 换成活跃的替代实现**：需要改模型与迁移，风险最高。
   - **c. 等上游**：目前看不到希望（最新版就是 1.8.3）。
2. `django-crispy-forms` 1.14 → 2.7，新增 `crispy-bootstrap4` 依赖，
   `CRISPY_TEMPLATE_PACK` 相关配置调整，**回归表单页视觉**（登录/注册/改资料/换头像/评论）。
3. `django-redis` 5.2 → 7.0，并在**真正启用 Redis** 的环境实测缓存读写与降级。
4. Django → 5.2.17，顺带确认 `USE_L10N`（5.0 已移除）可以删掉。
5. 回归：全量测试 + 核心页面冒烟 + `manage.py check --deploy`。

## 六、残余风险与当前补偿措施

7 条告警按"本项目是否真的会触发"逐个核对（描述取自 OSV）：

| 漏洞 | 严重度 | 触发条件 | 本项目 | 补偿 |
|------|--------|----------|--------|------|
| CVE-2026-48588 | LOW | `UpdateCacheMiddleware` / `cache_page()` 缓存"按 cookie 变化"的响应，请求携带无关 cookie 时可读到他人缓存 | **适用**：文章/图画列表页正是 `cache_page` + `vary_on_cookie` | ✅ 已实施：见下节 |
| CVE-2026-48587 | LOW | 响应的 `Vary` 头里含**首尾空格**导致比较失配 | 不适用：`Vary` 由 Django 自身写入，无空格填充 | 同上的缓存策略变更额外覆盖 |
| CVE-2026-8404 | LOW | 响应 `Cache-Control` 用了大写/混合大小写指令 | 不适用：项目未手写 `Cache-Control`，Django 输出全小写 | 同上 |
| CVE-2026-53878 | MEDIUM | `DomainNameValidator` 允许换行 → 头注入 | 不适用：项目未使用该校验器 | 无需处理 |
| CVE-2026-53877 | HIGH | `GDALRaster` 由 bytes 构造时堆越界读 | 不适用：未启用 GeoDjango / GDAL | 无需处理 |
| CVE-2026-6873 | LOW | 签名 cookie 的 salt 命名空间碰撞（需应用自行用 `signing` 且 salt 与 Django 冲突） | 不适用：项目未自行调用 `django.core.signing` | 无需处理 |
| PYSEC-2026-3717 | 未知（可用性） | 无公开摘要 | 未知 | 观察 |

> 注：OSV 的严重度评级与 GitHub dependabot 页面可能不一致，此处以 OSV 原始数据为准。

### 已实施的补偿：整页缓存只服务匿名访客

新增 `kaku/cache.py::cache_page_anonymous`，替换两个列表页的 `cache_page`：

```python
path('', cache_page_anonymous(60 * 10)(vary_on_cookie(views.IndexView.as_view())), name='index'),
```

理由：这两页的顶栏与右侧抽屉含**当前用户的昵称、头像、未读通知数**。
现在——

- **已登录请求**：直接进视图，渲染结果永不写入共享缓存；
- **匿名请求**：进缓存，但匿名渲染里没有任何私有数据，缓存键即使算错也无信息可泄露；
- `vary_on_cookie` 保留，作为与上面逻辑相互独立的一道防线。

这样就把 CVE-2026-48588 的"从共享缓存读私有数据"这一后果**在应用层消除**，
代价仅是登录用户列表页不再走整页缓存（首页/列表页仍是数据库查询，开销可控）。

回归测试见 `kaku/tests.py::CachePageAnonymousTests`（匿名命中缓存、登录必定新渲染、
登录响应不会落进共享缓存）。

## 七、复现探针

```powershell
# 取 Django 5.2 并旁挂（不改 venv）
.\venv\Scripts\python.exe scripts\probe_django.py 5.2.17

# 影子包：复制 notifications 并把 index_together 改成 indexes
New-Item -ItemType Directory -Force .tmp_probe | Out-Null
Copy-Item -Recurse -Force .\venv\Lib\site-packages\notifications .\.tmp_probe\notifications

$env:PYTHONPATH="<项目绝对路径>\.tmp_dj52;<项目绝对路径>\.tmp_probe"
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test --verbosity 1

# 探针结束：删掉 .tmp_dj52 / .tmp_probe / .tmp_pip（均已在 .gitignore 中忽略）
```

## 八、决策

| 方案 | 内容 | 结论 |
|------|------|------|
| **A（采纳）** | 暂缓 5.2，先做其它待办；把可行性结论与残余风险文档化，并对真正适用的那条告警做应用层缓解 | ✅ 保持依赖锁定约束不变 |
| B | 内联 fork notifications + 升 Django 5.2.17 | 留待单独立项 |
| C | 在 B 基础上再升 crispy-forms 2.7 + crispy-bootstrap4 + django-redis 7 | 表单页视觉回归面最大，优先级最低 |
