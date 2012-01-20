from django import template
from django.conf import settings

register = template.Library()


@register.filter(name='app_filter')
def app_filter(app_list):
    """ Remove apps from the admin interface """
    if hasattr(settings, 'ADMIN_APPS_EXCLUDE'):
        return [app for app in app_list \
                if app['name'] not in settings.ADMIN_APPS_EXCLUDE]
    return app_list

@register.filter(name='model_filter')
def model_filter(model_list):
    """ Remove apps from the admin interface """
    if hasattr(settings, 'ADMIN_MODELS_EXCLUDE'):
        return [model for model in model_list \
                if model['name'] not in settings.ADMIN_MODELS_EXCLUDE]
    return model_list
