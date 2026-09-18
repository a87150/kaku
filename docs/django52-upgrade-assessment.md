# Django 4.2 → 5.2 LTS 升级记录

> 结论：**已完升级**（Django 4.2.30 → 5.2.17）。剩余 7 条 dependabot 告警全部清零，
> 依赖审计从「45 个包 / 7 条命中」变为「**42 个包 / 0 条命中**」。
>
> 破局点：用社区维护的 `django-notifications-community` 替换已停更的
> `django-notifications-hq`——这是当初判定"无法只靠升级版本解决"的那个硬阻塞。
> 本文保留完整论证过程与实测证据，便于日后回看或回退。

---

## 一、背景：为什么必须动 Django

`docs/dependabot-audit.md` 里最后剩余的安全告警**全部是 Django**，且修复版本只存在于
5.2.x / 6.0.x 线——Django 4.2 已 EOL，不会再收到这些修复。
**不跨大版本，这些告警一条也清不掉。**

---

## 二、第一阶段：为什么最初判断"暂缓"

### 2.1 验证方法（全程不污染 venv）

不直接在项目 venv 里换 Django，而是把目标版本的 wheel 旁挂出来，用 `PYTHONPATH`
让它遮蔽 venv 里的版本。工具已沉淀为 `scripts/probe_django.py`：

```powershell
.\venv\Scripts\python.exe scripts\probe_django.py 5.2.17
$env:PYTHONPATH="$PWD\.tmp_dj52"
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test --verbosity 1
```

### 2.2 发现的唯一代码级阻塞

```
File "venv\Lib\site-packages\notifications\base\models.py", line 148, in AbstractNotification
    class Meta:
TypeError: 'class Meta' got invalid attribute(s): index_together
```

`django-notifications-hq 1.8.3` 的 `AbstractNotification.Meta` 用了 `index_together`，
而该选项在 **Django 5.1 被移除**。把它改成 `Meta.indexes` 后，5.2 下 `check` 干净、
测试全绿——说明**项目自身代码没有其它代码级阻塞**。

### 2.3 当时的结论

Django 能升，卡住的是 `django-notifications-hq`：它最新版就是 1.8.3（2023 年后停更，
上游无新版本），唯一的出路是"把它的源码内联进项目自己维护"。权衡后当时选择暂缓，
并对**真正会命中本项目**的那条告警做了应用层缓解（见第六节）。

---

## 三、破局点：django-notifications-community

| 项目 | 值 |
|------|-----|
| 包名 | `django-notifications-community` |
| 版本 | **1.12.2**（2026-08-19） |
| 定位 | 上游 `django-notifications/django-notifications` 的社区维护 fork |
| 依赖 | `django<6.3,>=5.2`（无 swapper / jsonfield / pytz） |
| 支持 | Django 5.2 / 6.0，Python 3.10–3.14 |
| 兼容性 | README 明确为 drop-in replacement，导入路径仍是 `import notifications` |

---

## 四、升级前的四项实证

### 4.1 迁移历史连续（决定能否保留现有数据）

community 的 `0001–0009` 与已安装的 hq **文件名逐个一致**，其后追加：

```
0010_rename_notification_recipient_unread_notificatio_recipie_8bedf2_idx
0011_replace_jsonfield_with_native
0012_gfk_indexes
0013_alter_notification_level
```

因此**不需要伪造任何迁移记录**。另外 community 在 0003 / 0009 里对 `jsonfield`
用了 try/except 垫片，所以卸载 `jsonfield` 也不会让历史迁移导入失败。

### 4.2 真实数据库副本上的数据迁移

复制 `db.sqlite3` 后跑 `migrate notifications`：

```
Applying notifications.0010... OK
Applying notifications.0011_replace_jsonfield_with_native... OK
Applying notifications.0012_gfk_indexes... OK
Applying notifications.0013_alter_notification_level... OK
MIGRATE OK

通知行数：迁移前 1 → 迁移后 1（数据未丢，列集合不变）
其它应用：No planned migration operations.
```

### 4.3 全链条旁挂测试

把这一整组旁挂后用临时 settings 跑全量：

| 组件 | 版本 |
|------|------|
| Django | 5.2.17（5.2 线最新） |
| django-notifications-community | 1.12.2 |
| django-crispy-forms | 2.7 |
| crispy-bootstrap5 | 2026.9 |
| django-redis | 7.0.0 |

结果：`check` 无问题、**114/114 全绿、零告警**。

### 4.4 项目用到的 API 面

`{% notifications_unread %}`、`AllNotificationsList`、`notify`、`notifications.urls`、
`Notification` 模型——全部保留。

---

## 五、实际执行的变更

### 5.1 依赖

| 包 | 变更 |
|----|------|
| Django | 4.2.30 → **5.2.17** |
| django-notifications-hq | 1.8.3 → **移除**，换成 django-notifications-community 1.12.2 |
| django-crispy-forms | 1.14.0 → **2.7** |
| crispy-bootstrap5 | 新增 **2026.9**（2.x 起模板包拆分为独立发行包） |
| django-redis | 5.2.0 → **7.0.0** |
| swapper / jsonfield / pytz / django-model-utils | **移除**（经反查，四者都只被 notifications-hq 需要） |

### 5.2 代码与配置

- `kaku/settings.py`
  - `INSTALLED_APPS` 增加 `crispy_bootstrap5`
  - `CRISPY_TEMPLATE_PACK` / `CRISPY_ALLOWED_TEMPLATE_PACKS` 改为 `bootstrap5`
  - 删除 `USE_L10N`（Django 5.0 已移除该设置）
- `common_static/css/bootstrap.min.css`：**Bootstrap 4.6.2 → 5.3.8**
- BS4 专属类 `.form-control-file`（BS5 已移除）迁移为 `.form-control`：
  `picture/forms.py`、`templates/users/profile.html`（CSS + markup）、
  `templates/picture/post_picture.html`（CSS）
- `kaku/compat_py314.py` **保留但已自动空转**：Django 5.2 上游把
  `BaseContext.__copy__` 从 `copy(super())` 改成了 `duplicate.__class__ = self.__class__`，
  补丁的源码自检不通过会直接 return。保留它是为了兼容回退到 4.2 的场景。

### 5.3 数据库

```bash
python manage.py migrate     # 应用 notifications.0010 - 0013
```

---

## 六、验证结果

| 项目 | 结果 |
|------|------|
| `manage.py check` | 无问题 |
| 全量测试 | **114/114 通过** |
| 依赖审计 | **42 个包 / 0 条命中**（此前 45 / 7） |
| 真实库迁移 | 0010–0013 全部 OK，通知数据无损 |
| crispy 实际产出 | 已确认为 Bootstrap 5 标记（`mb-3` / `form-label` / `form-text`，无 `form-group`） |
| `pip check` | No broken requirements found |

### 关于此前那条应用层缓解

上一阶段为 CVE-2026-48588（`cache_page` 缓存含用户信息的列表页）加过
`kaku/cache.py::cache_page_anonymous`——整页缓存只服务匿名访客。
**该缓解保留**：它本身是正确做法（匿名渲染无私有数据），与 Django 版本无关。

---

## 七、影响面与后续注意事项

1. **表单页需要浏览器目视回归**：登录 / 注册 / 改资料 / 换头像 / 评论 / 两个创作页。
   Bootstrap 4 → 5 与 crispy 1.x → 2.x 同时生效，自动化测试只覆盖渲染成功，覆盖不了观感。
2. **Redis 需要实机验证**：`django-redis 7.0` 的降级路径有测试覆盖（`kaku/redisfake.py`），
   但**真正跑着 Redis 的环境**要实测缓存读写。
3. **部署时**：`pip install -r requirements.txt` 后必须
   `python manage.py migrate`（notifications 有 4 条新迁移）并重启进程；
   静态资源变了（bootstrap.min.css），需重跑 `collectstatic`。
4. **回退**：`git revert` + 恢复 `db.sqlite3.bak-*` 备份 + 按旧 `requirements.txt` 重装。
   notifications 的 0010–0013 是向后兼容的（改名索引 / 换 JSON 字段类型 / 加索引），
   但回退到 hq 后其 `index_together` 与 5.x 不兼容，只能连同 Django 一起回退。

---

## 八、复现探针

```powershell
# 1) 旁挂任意 Django 版本（只依赖标准库，不碰 venv）
.\venv\Scripts\python.exe scripts\probe_django.py 5.2.17

# 2) 让旁挂版本遮蔽 venv
$env:PYTHONPATH="$PWD\.tmp_dj52"
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test --verbosity 1

# 3) 探针目录（.tmp_*）已在 .gitignore 中忽略，用完删除即可
```
