# Kaku - 个人博客网站

一个支持用 Markdown 写文章和上传图片分享的社区，实现了评论、关注、点赞、动态、通知、OAuth 等功能。

使用 Redis 作为缓存，实现了保存页面和点赞、点击功能。

## 项目信息

- **框架**: Django 5.2.17 (LTS)
- **Python 版本**: 3.10 – 3.14（Django 5.2 官方支持范围，本机 3.14.7 已在其中）
- **数据库**: SQLite（默认）或 MySQL
- **缓存**: Redis（可选，未安装 Redis 时自动回退到数据库）

## 功能特性

- 用户注册/登录（支持 GitHub OAuth）
- 文章发布与管理（Markdown 支持）
- 图片上传与展示
- 评论系统
- 关注用户
- 标签系统
- 点赞功能
- 搜索功能
- Redis 缓存支持（无 Redis 也可运行）
- 用户动态
- 通知系统

## 环境要求

- Python 3.12 或更高版本（推荐 3.12）
- Redis 服务器（可选，用于缓存加速）
- MySQL（可选，默认使用 SQLite）

## 快速开始

### Windows 用户

1. **创建虚拟环境并安装依赖**
   ```cmd
   python -m venv venv
   venv\Scripts\activate.bat
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

2. **运行数据库迁移**
   ```cmd
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **创建超级用户**
   ```cmd
   python manage.py createsuperuser
   ```

4. **启动开发服务器**
   ```cmd
   python manage.py runserver
   ```

### Linux/Mac 用户

1. **创建虚拟环境并安装依赖**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

2. **运行数据库迁移**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **创建超级用户**
   ```bash
   python manage.py createsuperuser
   ```

4. **启动开发服务器**
   ```bash
   python manage.py runserver
   ```

## 手动设置

### 1. 创建虚拟环境

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate.bat
```

### 2. 升级 pip

```bash
pip install --upgrade pip setuptools wheel
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 Redis（可选）

如果安装了 Redis，项目会自动使用它作为缓存；未安装也能正常运行（自动回退到数据库）。

```bash
redis-server
```

### 5. 运行迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 创建超级用户

```bash
python manage.py createsuperuser
```

### 7. 启动服务器

```bash
python manage.py runserver
```

## 管理命令

```bash
# 收集静态文件
python manage.py collectstatic

# 同步缓存到数据库
python manage.py sync_cache

# 创建数据库脚本
python manage.py makemigrations

# 创建数据库
python manage.py migrate

# 创建管理员账号
python manage.py createsuperuser

# 启动服务器
python manage.py runserver
```

## 配置说明

### 数据库配置

默认使用 SQLite。如需切换 MySQL，修改 `kaku/settings.py` 中的 `DATABASES` 配置，
并自行安装 `mysqlclient`（当前 `requirements.txt` 锁定的是 SQLite 部署，未包含它）：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Redis 配置

Redis 配置在 `kaku/settings.py` 中：

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "KEY_PREFIX": "example",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "socket_connect_timeout": 0.3,
            },
            # Redis 不可用时静默降级，不拖慢页面
            "IGNORE_EXCEPTIONS": True,
        }
    }
}
```

### 环境变量配置（推荐）

从 v3.1 起，敏感配置改为通过环境变量注入，不再硬编码在代码里。
本地开发：复制 `.env.example` 为 `.env` 并填入你自己的值（.env 已被 git 忽略）：

```bash
cp .env.example .env   # 然后编辑 .env
```

支持的环境变量：

| 变量 | 用途 | 示例 |
|------|------|------|
| `DJANGO_SECRET_KEY` | Django 密钥（生产必改） | 一长串随机字符 |
| `DJANGO_DEBUG` | `True`/`False` | 生产设为 `False` |
| `DJANGO_ALLOWED_HOSTS` | 逗号分隔主机名 | `mydomain.com,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | HTTPS 站点必填，否则登录等 POST 报 403 | `https://mydomain.com` |
| `DJANGO_HTTPS` | `1` 时启用 SSL 跳转/安全 Cookie/HSTS（默认关） | `1` |
| `DJANGO_HSTS_SECONDS` | HSTS 有效期（配合上一项） | `31536000` |
| `GITHUB_CLIENTID` | GitHub OAuth Client ID | — |
| `GITHUB_CLIENTSECRET` | GitHub OAuth Client Secret | — |
| `GITHUB_CALLBACK` | GitHub OAuth 回调地址 | `http://127.0.0.1:8000/oauth/github/` |

> `DJANGO_HTTPS` 特意做成显式开关而不是"DEBUG=False 就自动开"：若 nginx 只监听 80 端口，
> 自动开启 `SECURE_SSL_REDIRECT` 会造成 http → https 的重定向环，站点直接打不开。

或在 shell 中直接 export（Linux/Mac）或 `$env:`（Windows PowerShell）后运行。

### GitHub OAuth 配置

1. 在 [GitHub OAuth Apps](https://github.com/settings/developers) 创建应用
2. 把 Client ID / Secret / 回调地址填入 `.env`（见上表）

### 允许的主机

默认已含 `127.0.0.1`、`localhost`、`takanashi.site`；如需更多，通过环境变量 `DJANGO_ALLOWED_HOSTS` 或直接编辑 `kaku/settings.py` 中 `ALLOWED_HOSTS` 设置。

### 安全配置

生产环境中务必：

1. 通过 `DJANGO_SECRET_KEY` 注入随机密钥
2. 设置 `DJANGO_DEBUG=False`
3. 配置静态文件服务（`collectstatic` + nginx）
4. 配置邮件后端（邮件在 `.env` 对应 SMTP 或 settings 修改）

## 生产部署

nginx + gunicorn + supervisor 的完整流程见 **[`deploy/README.md`](deploy/README.md)**，
配套示例配置在 `deploy/` 下（`nginx.conf` / `gunicorn_start.sh` / `supervisor.conf`）。
该文档涵盖：环境变量清单、首次部署步骤、升级与回滚、Redis 降级与 `sync_cache` 定时任务、
备份方式、上线检查清单。

## 项目结构

```
kaku/
├── kaku/              # 项目配置
├── users/             # 用户应用
├── written/           # 文章应用
├── picture/           # 图片应用
├── comment/           # 评论应用
├── follow/            # 关注应用
├── oauth/             # OAuth 认证
├── search/            # 搜索功能
├── index/             # 首页和通用功能
├── common_static/     # 静态资源
├── templates/         # 模板文件
├── media/             # 媒体文件
├── static/            # 静态文件收集目录
└── manage.py          # Django 管理脚本
```

## 依赖包版本

| 包名 | 版本 | 说明 |
|------|------|------|
| Django | 5.2.17 | Web 框架 (LTS) |
| django-allauth | 65.19.2 | 认证系统（0.63+ 新设置风格） |
| django-crispy-forms | 2.7 | 表单渲染 |
| crispy-bootstrap5 | 2026.9 | crispy 2.x 起模板包拆分为独立发行包（表单页用 Bootstrap 5.3.8） |
| django-imagekit | 6.1.0 | 图片处理 |
| django-notifications-community | 1.12.2 | 通知系统（社区维护 fork，替代已停更的 django-notifications-hq） |
| django-simple-captcha | 0.7.0 | 验证码 |
| django-activity-stream | 2.0.0 | 活动流 |
| django-redis | 7.0.0 | Redis 缓存 |
| mistune | 3.3.4 | Markdown 解析（已启用 table / strikethrough 插件，与编辑器工具栏一致） |
| Pillow | 12.3.0 | 图像处理 |
| bleach | 6.4.0 | HTML 清理 |
| sqlparse | 0.6.0 | SQL 解析（Django 依赖） |
| setuptools | 84.0.0 | 构建/打包工具 |

## 依赖安全审计

`scripts/dep_audit.py` 会把当前虚拟环境中**全部已安装包**（含传递依赖）提交
[OSV 漏洞库](https://osv.dev/) 比对，生成明细清单：

```bash
python scripts/dep_audit.py docs/dependabot-audit.md
```

最近一次审计结果见 [`docs/dependabot-audit.md`](docs/dependabot-audit.md)：
**42 个包、0 条命中**。

沿革：最初有 72 条告警，经 mistune（28 条）、django-allauth（6 条）、setuptools（4 条）
等升级清零后，最后剩余 7 条**全部来自 Django 4.2.30**——4.2 已 EOL，这些修复只发在
5.2/6.0 线，而依赖链上又有一个已停更的组件卡着。这 7 条已随
**Django 4.2 → 5.2.17** 的升级全部清除。

## 常见问题

### Q: 依赖安装失败

A: 确保 Python 版本是 3.12+，并使用虚拟环境。

### Q: Redis 连接失败 / 未安装 Redis

A: 项目已做降级处理：Redis 不可用时自动回退到数据库操作，页面不会报错。若需要使用 Redis 缓存加速，确保 Redis 服务器运行在 127.0.0.1:6379 即可。

### Q: 数据库迁移错误

A: 全新项目直接运行 `python manage.py makemigrations` 和 `python manage.py migrate` 即可；旧数据建议先备份。

### Q: 静态文件无法加载

A: 运行 `python manage.py collectstatic`。

### Q: Python 3.13 / 3.14 下是否支持

A: 支持。项目现运行在 Django 5.2.17 上，5.2 官方支持 Python 3.10–3.14。

## 更新日志

### v3.3 — Django 5.2 LTS 升级 + 通知组件换血 + Bootstrap 5

**Django 4.2.30 → 5.2.17**，剩余 7 条 dependabot 告警全部清零（审计结果 42 个包 / 0 条命中）。

- 通知组件：`django-notifications-hq 1.8.3`（已停更，`Meta` 里用了 Django 5.1 移除的
  `index_together`，正是在 5.2 上的硬阻塞）换成社区维护的
  **`django-notifications-community 1.12.2`**。导入路径仍是 `notifications`，
  迁移历史与旧版**连续**（0001–0009 文件名一致，新增 0010–0013），已实测在真实库上
  平滑迁移、通知数据不丢
- 表单渲染：`django-crispy-forms 1.14.0 → 2.7`；2.x 起模板包拆分为独立发行包，
  本项目表单页改用 **Bootstrap 5**，因此引入 `crispy-bootstrap5 2026.9`，
  `CRISPY_TEMPLATE_PACK` / `CRISPY_ALLOWED_TEMPLATE_PACKS` 相应改为 `bootstrap5`
- 静态资源：`common_static/css/bootstrap.min.css` 由 **Bootstrap 4.6.2 → 5.3.8**；
  同步迁移 BS4 专属类 `.form-control-file`（BS5 已移除，文件输入统一用 `.form-control`）
- 缓存：`django-redis 5.2.0 → 7.0.0`（redis-py 已是 8.1.0，无需变更）
- 清理孤儿依赖：`swapper` / `jsonfield` / `pytz` / `django-model-utils` 均只因
  notifications-hq 而存在，换包后一并卸载并移出 `requirements.txt`
- Python 版本回到官方支持范围：Django 5.2 官方支持 3.10–3.14（4.2 只到 3.12，
  此前靠一份内置补丁兜底）
- 移除 `USE_L10N`（Django 5.0 已删除该设置）
- 清理 4.2 时代的兼容负担：删除 `kaku/compat_py314.py`（5.2 上游已修掉它要绕过的
  `BaseContext.__copy__`）与版本探针脚本，并清掉 settings 里遗留的旧版文档链接、
  Django 1.10 样板注释、`oauth` 里的空壳测试
- 测试 114 项全绿，`manage.py check` 无问题

### v3.2 — 前端体验 / 功能增强 / 部署文档化

- **前端按需加载**：bootstrap 原先全站加载（158KB），现改为只在含表单或评论表单的
  7 个页面引入（新增 `templates/includes/_bootstrap_css.html` + base.html 的
  `base_css` 块），浏览页不再白付这份体积
- **创作页移动端适配**：文章编辑器页与发布图画页在窄屏收紧内边距、降低编辑区高度、
  放大工具按钮触控区、输入框字号提升到 16px（避免 iOS 聚焦自动放大页面）、
  画板弹层窄屏占满整屏
- **详情页标签即时增删**：新增 `POST /tags/delete/`（仅作者本人可移除，前端不发请求
  也能看到完整标签）；新增 `common_static/js/kaku-tags-live.js` 用 DOM 就地增删，
  不再 `location.reload()`；服务端同时补上标签长度校验并回传最终标签名
- **画板以已有图片为底再创作**：Painterro 的 `show(字符串)` 会把该图载入画布
  （`show({})` 才是清空），已选图片时按钮文案变为「在所选图片上继续画」
- **搜索体验**：结果区分「文章 / 图画」徽标、关键词高亮（`highlight` 过滤器）、
  显示命中条数与截断提示、关键词去首尾空格、非法 `type` 回退为 `all`
- **列表页**：卡片显示点赞/评论数（`annotate` 一次聚合，避免 N+1）、标签链接
  `urlencode`、分页链接保留查询参数（新增 `{% page_url %}` 标签）
- **安全（Django 4.2 无补丁项的补偿）**：整页缓存改为只服务匿名访客
  （`kaku/cache.py::cache_page_anonymous`），使 CVE-2026-48588 在本项目失去适用面
- **配置**：`CSRF_TRUSTED_ORIGINS` 与 `DJANGO_HTTPS` 安全开关（默认全关，避免纯 HTTP
  部署出现重定向环）；`.env.example` 同步补齐
- **文档**：新增 `deploy/README.md`（生产部署指南）
- 测试 83 → 109 项，`manage.py check` 无问题

### v3.1 — 依赖安全补丁升级（dependabot）

- Django 4.2.11 → 4.2.30（4.2 LTS 内全部安全修复批次，含 CVE-2024-38875 / CVE-2024-45230~32 / CVE-2024-53907~09 等）
- django-allauth 0.61.0 → 0.63.6（0.x 线末尾，覆盖历次安全公告；未升 64/65 大改动线）
- django-simple-captcha 0.6.0 → 0.7.0
- sqlparse 0.4.4 → 0.6.0（修复 CVE-2024-43485 ReDoS）
- setuptools 69.5.1 → 70.1.1（修复 CVE-2024-6345；勿再升 ≥84，其已移除 pkg_resources）
- bleach 6.0.0 → 6.4.0（6.x 安全修复线）
- django-notifications-hq 1.8.0 → 1.8.3（1.8 线安全/兼容修复）
- django-model-utils 4.2.0 → 5.0.0 + setuptools 70.1.1 → 84.0.0：
  model-utils 5.0 改用 importlib.metadata，解除了对 pkg_resources 的依赖，
  setuptools 因此可升到最新（原先被迫停留在 70.1.1）
- mistune 2.0.4 → 3.3.4：一次性消除 28 条 XSS / ReDoS 公告（其修复版本仅存在于
  3.x）；同时启用 table / strikethrough 插件，修复了“编辑器插入的 GFM 表格
  在详情页不渲染”的老问题（表格对齐由 style 转成安全的 align 属性保留）
- django-allauth 0.63.6 → 65.19.2：消除 6 条公告（open redirect 等），并迁移到
  0.63+ 新设置风格：
  * `ACCOUNT_AUTHENTICATION_METHOD` → `ACCOUNT_LOGIN_METHODS = {'username', 'email'}`
  * `ACCOUNT_EMAIL_REQUIRED` → `ACCOUNT_SIGNUP_FIELDS = ['username*', 'email*', 'password1*', 'password2*']`
  * `ACCOUNT_USERNAME_VALIDATORS` 改为「指向 list 的路径」
    （`users.validators.username_validators`），否则注册会直接 500
- Pillow / requests 已是最新安全版本，未改动
- 移除停更的 django-pagedown（编辑器已改用 EasyMDE）
- 升级后 `manage.py check` 无问题，79 项测试全绿

### v3.0 — Django 4.2 升级

- 升级 Django 至 4.2.11 LTS
- URL 路由迁移至 `path()` / `re_path()`
- 移除 `ugettext`/`force_text` 等旧 API
- 移除已停更的 django-bootstrap-pagination，改用内置分页模板
- imagekit / actstream 升级到兼容版本（含 Python 3.14 修复）
- Redis 降级支持：无 Redis 也能完整运行
- 添加 Python 3.13/3.14 兼容补丁
- 生成 Django 4.2 所需的迁移文件

### v2.0 (2024-01-01)

- 修复依赖版本问题
- 添加详细文档和配置说明

### v1.0 (原始版本)

- 初始版本，支持基本的博客和社交功能

## 许可证

本项目仅供学习和个人使用。

## 注意事项

- 这是一个早期的学习项目，代码可能不够规范
- 注意修改默认的 SECRET_KEY 和敏感配置
- 若使用 MySQL，需要额外安装 mysqlclient 并修改 DATABASES 配置

---

好きなことをかく (喜欢做什么就写什么)

powered by django