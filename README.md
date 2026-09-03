# Kaku - 个人博客网站

一个支持用 Markdown 写文章和上传图片分享的社区，实现了评论、关注、点赞、动态、通知、OAuth 等功能。

使用 Redis 作为缓存，实现了保存页面和点赞、点击功能。

## 项目信息

- **框架**: Django 4.2.11 (LTS)
- **Python 版本**: 3.12+（Django 4.2 官方支持 3.8-3.12；在 Python 3.13/3.14 上需依赖项目内置的 `kaku/compat_py314.py` 兼容补丁，项目已自动加载）
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

默认使用 SQLite，生产环境建议使用 MySQL。

修改 `kaku/settings.py` 中的 `DATABASES` 配置：

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

如果不使用 MySQL，可以从 `requirements.txt` 中删除 `mysqlclient==1.3.14`。

### Redis 配置

Redis 配置在 `kaku/settings.py` 中：

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "KEY_PREFIX": "kaku",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
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
| `GITHUB_CLIENTID` | GitHub OAuth Client ID | — |
| `GITHUB_CLIENTSECRET` | GitHub OAuth Client Secret | — |
| `GITHUB_CALLBACK` | GitHub OAuth 回调地址 | `http://127.0.0.1:8000/oauth/github/` |

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
| Django | 4.2.11 | Web 框架 (LTS) |
| django-allauth | 0.61.0 | 认证系统 |
| django-crispy-forms | 1.14.0 | 表单渲染 |
| django-imagekit | 6.1.0 | 图片处理 |
| django-notifications-hq | 1.8.0 | 通知系统 |
| django-simple-captcha | 0.6.0 | 验证码 |
| django-pagedown | 2.2.1 | Markdown 编辑器 |
| django-activity-stream | 2.0.0 | 活动流 |
| django-redis | 5.2.0 | Redis 缓存 |
| mistune | 2.0.4 | Markdown 解析 |
| Pillow | 12.3.0 | 图像处理 |
| bleach | 6.0.0 | HTML 清理 |
| sqlparse | 0.4.4 | SQL 解析（Django 依赖） |
| setuptools | 69.5.1 | 提供 pkg_resources |

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

A: Django 4.2 官方支持 Python 3.8-3.12。项目已在 `kaku/compat_py314.py` 内置兼容补丁（随 settings 自动加载），可在 Python 3.13/3.14 上运行；推荐使用 Python 3.12 获得最佳兼容性。

## 更新日志

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