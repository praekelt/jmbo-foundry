import re

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user

from django.http import HttpResponseRedirect

from preferences import preferences


class VerboseRequestMeta:
    """Add metadata to request so repr(request) prints more information. Runs
    as one of the last middleware."""

    def process_request(self, request):
        user = getattr(request, 'user', None)
        if user is not None:
            request.META['AUTHENTICATED_USER'] = str(user)


class AgeGateway:
    """Redirect if age gateway is enabled and user is anonymous. Must run after
    AuthenticationMiddleware."""

    def process_response(self, request, response):
        # Already passed gateway
        if request.COOKIES.get('age_gateway_passed'):
            return response

        exempted_urls = (
            reverse('age-gateway'), reverse('join'), reverse('login'), 
            '/password_reset', '/static', '/admin'
        )

        # On an exempted url
        if re.match(r'|'.join(exempted_urls), request.META['PATH_INFO']) is not None:
            return response

        user = getattr(request, 'user', None)
        # xxx: investigate preference caching
        if (user is not None) and user.is_anonymous() and preferences.GeneralPreferences.show_age_gateway:
            return HttpResponseRedirect(exempted_urls[0])

        return response            


class PaginationMiddleware:
    """Our replacement for django-pagination PaginationMiddleware. It defaults
    to the last page if no page is set on the request. A monkey patch in
    monkey.py handles the negative page number."""

    def process_request(self, request):       
        page = -1
        try:
            page = int(request.REQUEST['page'])
        except (KeyError, ValueError, TypeError):
            pass
        request.__class__.page = page
        
class MembersOnlineStatusMiddleware(object):
    """Cache MembersOnlineStatus instance for an authenticated member"""
    
    def process_request(self, request):
        
        MEMBERS_ONLINE_CACHE_TAG = 'MEMBERS_ONLINE'
        
        user = get_user(request)
        
        if not user.is_authenticated() and hasattr(user,'member'):
            return
        
        MEMBER_ONLINE_CACHE_TAG = 'USER_%d_MEMBER_ONLINE' % user.id
        
        cache.set(MEMBER_ONLINE_CACHE_TAG, 
                  MEMBER_ONLINE_CACHE_TAG, 
                  settings.MEMBERS_ONLINE_TIMEOUT)
        
        online_members = cache.get(MEMBERS_ONLINE_CACHE_TAG)
        
        if not online_members:
            online_members = []
            
        if MEMBER_ONLINE_CACHE_TAG not in online_members:
            online_members.append(MEMBER_ONLINE_CACHE_TAG)
        
        for member_id in online_members:
            if not cache.get(member_id):
                online_members.remove(member_id)
                
        cache.set(MEMBERS_ONLINE_CACHE_TAG, 
                  online_members, 
                  settings.MEMBERS_ONLINE_TIMEOUT * 5)
        
        return
