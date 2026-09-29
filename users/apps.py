from django.apps import AppConfig
from django.db.models.signals import post_save


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('User'))

        from allauth.account.signals import user_logged_in, user_signed_up
        from .receivers import create_default_mugshot, record_last_login_ip, update_joined
        post_save.connect(create_default_mugshot, sender=self.get_model('User'),
                          dispatch_uid='users.create_default_mugshot')
        user_signed_up.connect(update_joined)
        user_logged_in.connect(record_last_login_ip)
