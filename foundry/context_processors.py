from django.contrib.sites.models import get_current_site
from django.db.models import F
from django.conf import settings
from foundry.models import PageImpression, UserAgent
from preferences import preferences

def foundry(request):
    
    if not '/admin/' in request.path_info:
        
        ua, created = UserAgent.objects.get_or_create(user_agent=request.META['HTTP_USER_AGENT'])
        UserAgent.objects.filter(pk=ua.pk).update(hits=F('hits')+1)
        
        if request.user.is_authenticated():
            PageImpression.objects.create(path=request.path_info,
                                      user_agent=request.META['HTTP_USER_AGENT'],
                                      user=request.user)
        else:
            PageImpression.objects.create(path=request.path_info,
                                      user_agent=request.META['HTTP_USER_AGENT'])
    
    return {
        'FOUNDRY': settings.FOUNDRY,
        'LAYER_PATH': settings.FOUNDRY['layers'][0] + '/',
        'CURRENT_SITE': get_current_site(request),
        'ANALYTICS_TAGS': preferences.GeneralPreferences.analytics_tags,
        'DEFAULT_META_DESCRIPTION': preferences.GeneralPreferences.meta_description,
    }
