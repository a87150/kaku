from django.apps import AppConfig


class FollowConfig(AppConfig):
    name = 'follow'
    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Follow'))