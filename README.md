好きなことをかく

powered by django

一个支持用markdown写文章和上传图片分享的社区，实现了评论、关注、点赞、动态、通知、OAuth等功能。

使用redis作为缓存，实现了保存页面和点赞、点击功能。

django更新之后出了好多bug，比如没有six这个包了。


>首先执行 pip install -r requirements.txt   安装需要的包，不用MySQL可以删除 mysqlclient

>然后运行 python manage.py makemigrations   创建数据库脚本

>再运行   python manage.py migrate          创建数据库

>接着用   python manage.py createsuperuser  创建管理员账号

>最后用   python manage.py runserver        启动

>可以用   python manage.py collectstatic    收集静态文件

>还可以用 python manage.py sync_cache       同步缓存到数据库