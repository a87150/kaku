# Kaku 生产部署指南

面向把这套 Django 站点放到一台 Linux 服务器（nginx + gunicorn + supervisor）的完整流程。
本文档与 `deploy/` 下的三个示例配置配套：`gunicorn_start.sh`、`supervisor.conf`、`nginx.conf`。

> 示例里的路径统一假设为 `/django/kaku`（项目根）、运行用户 `kk`、组 `django`。
> 请按你的实际环境替换；Windows 本地开发不需要看这份文档。

---

## 1. 环境要求

| 组件 | 版本 / 说明 |
|------|-------------|
| Python | **3.14.x**（Django 5.2 官方支持 3.10–3.14） |
| Django | 5.2.17 LTS（见 `requirements.txt`，版本已锁定，勿随意回退） |
| 数据库 | SQLite（`db.sqlite3`），随项目目录 |
| Redis | **可选**。不可用时点赞/浏览量自动回退到数据库（见第 8 节） |
| Web 服务器 | nginx（静态/媒体文件 + 反代） |
| 应用服务器 | gunicorn（unix socket） |
| 进程守护 | supervisor（或 systemd） |

---

## 2. 首次部署步骤

```bash
# 1) 取代码
git clone git@github.com:a87150/kaku.git /django/kaku
cd /django/kaku

# 2) 建虚拟环境并安装依赖（版本已锁，全部按 requirements.txt）
python3.14 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3) 配置环境变量（敏感值一律走 .env，且 .env 已被 git 忽略）
cp .env.example .env
$EDITOR .env

# 4) 建表并建管理员
python manage.py migrate
python manage.py createsuperuser

# 5) 修正站点域名（django.contrib.sites，SITE_ID=1）
python manage.py shell -c "from django.contrib.sites.models import Site; \
s=Site.objects.get(pk=1); s.domain='takanashi.site'; s.name='kaku'; s.save()"

# 6) 收集静态文件到 STATIC_ROOT（= 项目下的 static/）
python manage.py collectstatic --noinput

# 7) 自检
python manage.py check --deploy     # 逐条核对安全项
```

**每次发布改动静态资源后都必须重跑 `collectstatic`**，否则页面会引用到旧文件。

---

## 3. 环境变量清单（`.env`）

settings 会在启动时读取项目根目录的 `.env`（自实现轻量解析，不覆盖已有环境变量）。

| 变量 | 必填 | 说明 |
|------|------|------|
| `DJANGO_SECRET_KEY` | 生产必填 | 随机长串。缺省值仅供本地开发 |
| `DJANGO_DEBUG` | 生产必填 `False` | 留空/`True` 会暴露调用栈与配置 |
| `DJANGO_ALLOWED_HOSTS` | 必填 | 逗号分隔，如 `takanashi.site,www.takanashi.site` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | HTTPS 必填 | 带协议的完整来源，如 `https://takanashi.site`。**不填会导致登录/点赞等 POST 报 403** |
| `DJANGO_HTTPS` | HTTPS 时填 `1` | 打开 SSL 跳转、安全 Cookie、HSTS |
| `DJANGO_HSTS_SECONDS` | 可选 | 默认 `31536000`（1 年） |
| `GITHUB_CLIENTID` / `GITHUB_CLIENTSECRET` | 需要 GitHub 登录时 | 在 GitHub OAuth App 里创建 |
| `GITHUB_CALLBACK` | 同上 | 必须与 GitHub 后台填的回调地址**完全一致**，如 `https://takanashi.site/oauth/github/` |

生成密钥：

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 关于 `DJANGO_HTTPS` 为什么是开关而不是自动

`nginx.conf` 示例只监听 80 端口。若照着“DEBUG=False 就自动开 HTTPS 安全项”的常见做法，
`SECURE_SSL_REDIRECT` 会把 http 请求跳到 https，而 443 没有监听者 —— 站点直接打不开（重定向环）。
所以本项目把这一组开关交给 `DJANGO_HTTPS` 显式控制：**先把 443 + 证书配好，再置 1**。

---

## 4. gunicorn

示例脚本 `deploy/gunicorn_start.sh`（请修改顶部路径/用户/组）：

```bash
NAME='kaku_app'
DJANGODIR=/django/kaku
SOCKFILE=/django/run/gunicorn.sock
USER=kk
GROUP=django
NUM_WORKERS=3
```

worker 数经验值 `2 × CPU 核数 + 1`；本项目是 SQLite，**不要开太高并发**，
`NUM_WORKERS` 建议 2–4，写操作（发文章/评论）由 SQLite 串行化。

发布新版本后需要重启：

```bash
supervisorctl restart kaku
```

---

## 5. supervisor

`deploy/supervisor.conf`：

```ini
[program:kaku]
command = /django/deploy/gunicorn_start.sh
user = kk
stdout_logfile = /django/logs/gunicorn_supervisor.log
redirect_stderr = true
```

推荐补充的常用项（示例里为保持简洁未写死）：

```ini
autostart = true
autorestart = true
stopasgroup = true
killasgroup = true
```

---

## 6. nginx

`deploy/nginx.conf` 已包含：静态/媒体目录直出、`client_max_body_size`、反代头透传
（含 `X-Forwarded-Proto`，配合 `DJANGO_HTTPS=1` 使用）。

上线前建议补齐：

1. **gzip**：mdui/easymde 等 CSS/JS 体积较大，开启 gzip 收益明显。
2. **缓存头**：`/static/` 加长缓存（改动靠 `collectstatic` + 文件名/查询串区分）；
   `/media/` 建议 `expires 30d`，但用户上传目录**不要**设 `add_header Cache-Control immutable`。
3. **上传目录权限**：nginx 只需读权限，写权限只能给 gunicorn 运行用户。
4. **HTTPS**：证书配好后加 443 server 块，再把 80 块改成 301 跳转到 https。

---

## 7. 升级与回滚

```bash
cd /django/kaku
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check
supervisorctl restart kaku
```

回滚：

```bash
git checkout <上一个可用提交>
pip install -r requirements.txt
python manage.py migrate <app> <上一个迁移号>   # 仅当本次带迁移时
supervisorctl restart kaku
```

> **升级前务必先备份 `db.sqlite3`**（SQLite 没有在线增量备份，见第 9 节）。

---

## 8. Redis 与降级行为

`settings.CACHES` 指向 `redis://127.0.0.1:6379/1`，并设置了 `IGNORE_EXCEPTIONS=True`
与会话级短超时（`socket_connect_timeout=0.3`，关闭重试退避）。

`index/redis_caches.py` 的每个函数都捕获 `ConnectionInterrupted / RedisError` 并在异常时
直接读写数据库，因此：

- **Redis 没装或挂掉，站点仍然可用**，只是点赞/浏览量直接落库（请求里多几次写 SQL）。
- 恢复 Redis 后，历史计数不会再重复写回：需要定时任务把差值同步到数据库：

```bash
python manage.py sync_cache     # 同步浏览量与点赞集合，然后清空对应 Redis 键
```

建议 crontab（例如每 10 分钟）：

```cron
*/10 * * * * cd /django/kaku && venv/bin/python manage.py sync_cache >> /django/logs/sync_cache.log 2>&1
```

**不跑 `sync_cache` 的后果**：浏览量/点赞数只存在于 Redis，Redis 一旦清空就丢计数。

---

## 9. 备份

核心资产只有三样：

| 内容 | 路径 | 说明 |
|------|------|------|
| 数据库 | `db.sqlite3` | 全部用户、文章、评论、标签 |
| 用户上传 | `media/` | 头像、图画题图 |
| 配置 | `.env` | 密钥与 OAuth 凭据（不在 git 里） |

SQLite 建议用官方 `.backup` 命令做一致性快照（直接 `cp` 正在写入的库可能拿到损坏副本）：

```bash
sqlite3 /django/kaku/db.sqlite3 ".backup '/django/backup/db-$(date +%F).sqlite3'"
tar czf /django/backup/media-$(date +%F).tar.gz -C /django/kaku media
```

---

## 10. 上线检查清单

- [ ] `DJANGO_DEBUG=False`
- [ ] `DJANGO_SECRET_KEY` 是随机长串（不是示例里的 `change-me...`）
- [ ] `DJANGO_ALLOWED_HOSTS` 只列真实域名
- [ ] HTTPS 站点已填 `DJANGO_CSRF_TRUSTED_ORIGINS`
- [ ] 已跑 `python manage.py check --deploy`，无 `W0xx` 告警
- [ ] 已跑 `python manage.py collectstatic --noinput`
- [ ] `media/` 与 `db.sqlite3` 的属主是 gunicorn 运行用户
- [ ] `/django/kaku/.env` 权限 `600`
- [ ] 已建 `sync_cache` 定时任务（使用 Redis 时）
- [ ] 验证过：注册、登录、GitHub 登录、发文章、发图画（含在线画板）、评论 @提及、点赞、标签增删、搜索

---

## 11. 本地开发（对照参考）

```powershell
.\venv\Scripts\python.exe manage.py runserver
.\venv\Scripts\python.exe manage.py test --verbosity 1
.\venv\Scripts\python.exe scripts\dep_audit.py docs\dependabot-audit.md
```

注意：**不要用 PowerShell 的 `Set-Content` 覆写含中文的 UTF-8 文件**
（历史上曾因此损坏 `requirements.txt` 的中文注释），统一用编辑器/文件编辑工具改。
