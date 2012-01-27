from django.contrib.sites.models import get_current_site
from django.conf import settings

from preferences import preferences

def foundry(request):
    return {
        'FOUNDRY': settings.FOUNDRY,
        'LAYER_PATH': settings.FOUNDRY['layers'][0] + '/',
        'CURRENT_SITE': get_current_site(request),
        'ANALYTICS_TAGS': preferences.GeneralPreferences.analytics_tags
    }
