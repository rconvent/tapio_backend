from django.apps import apps

for model in apps.get_app_config("tapio").get_models():

    if hasattr(model, "connect"):
        model.connect()