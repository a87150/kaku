好きなことをかく

先运行 python manage.py makemigrations  创建数据库脚本
再运行 python manage.py migrate         创建数据库
接着用 python manage.py createsuperuser 创建管理员账号
最后用 python manage.py runserver       启动