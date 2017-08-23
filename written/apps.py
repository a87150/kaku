from django.apps import AppConfig


class WrittenConfig(AppConfig):
    name = 'written'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Article'))
        registry.register(self.get_model('Chapter'))