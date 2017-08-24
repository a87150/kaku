from django.apps import AppConfig


class PictureConfig(AppConfig):
    name = 'picture'
    
    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Picture'))