from django.apps import AppConfig


class TapioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tapio'

    def ready(self):
        import tapio.signals

