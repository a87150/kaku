#!/bin/bash
# Kaku gunicorn 启动脚本（示例，供生产部署参考）
# 使用时请按环境修改路径/用户/组
NAME='kaku_app'
DJANGODIR=/django/kaku                 # Django 项目目录
SOCKFILE=/django/run/gunicorn.sock     # gunicorn socket 路径
USER=kk                                # 运行用户
GROUP=django                           # 运行组
NUM_WORKERS=3                          # worker 进程数
DJANGO_SETTINGS_MODULE=kaku.settings
DJANGO_WSGI_MODULE=kaku.wsgi

echo "starting $NAME as `whoami`"

# 激活 python 虚拟环境（按实际路径调整，例如 venv/bin/activate）
cd $DJANGODIR
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
# 生产请设置：export DJANGO_DEBUG=False 与 DJANGO_SECRET_KEY=<随机串>

# 创建 socket 目录
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# 启动 Django
exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --user=$USER --group=$GROUP \
    --log-level=info \
    --bind=unix:$SOCKFILE
