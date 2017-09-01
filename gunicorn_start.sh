#!/bin/bash
NAME='kaku_app'                         #应用的名称
DJANGODIR=/django/kaku                 	#django项目的目录
SOCKFILE=/django/run/gunicorn.sock     	#使用这个sock来通信
USER=kk                                    #运行此应用的用户
GROUP=django                                #运行此应用的组
NUM_WORKERS=3                                #gunicorn使用的工作进程数
DJANGO_SETTINGS_MODULE=kaku.settings         #django的配置文件
DJANGO_WSGI_MODULE=kaku.wsgi                 #wsgi模块

echo "starting $NAME as `whoami`"

#激活python虚拟运行环境
cd $DJANGODIR
source ../bin/activate
export  DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

#如果gunicorn.sock所在目录不存在则创建
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

#启动Django

exec ../bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --user=$USER --group=$GROUP \
    --log-level=debug \
    --bind=unix:$SOCKFILE