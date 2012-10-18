import re

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from preferences import preferences


PROTECTED_URLS_PATTERN = r'|'.join((
    reverse('age-gateway'), 
    reverse('join'), 
    reverse('login'), 
    reverse('terms-and-conditions'), 
    '/auth/password_reset', 
    '/static', 
    '/admin'
))


class VerboseRequestMeta:
    """Add metadata to request so repr(request) prints more information. Runs
    as one of the last middleware."""

    def process_request(self, request):
        user = getattr(request, 'user', None)
        if user is not None:
            request.META['AUTHENTICATED_USER'] = str(user)


class AgeGateway:
    """Combined private site and age gateway. Due to legacy this name is used.
    Must run after AuthenticationMiddleware."""

    def process_response(self, request, response):
        
        # Ignore ajax
        if request.is_ajax():
            return response
        
        # Protected URLs
        if re.match(PROTECTED_URLS_PATTERN, request.META['PATH_INFO']) is not None:
            return response

        # Listing feeds also exempted
        # todo: make the test more refined.
        if request.META['PATH_INFO'].endswith('/feed/'):
            return response

        # Now only do we hit the database
        # xxx: investigate preference caching. May want to hit the db less.
        private_site = preferences.GeneralPreferences.private_site
        show_age_gateway = preferences.GeneralPreferences.show_age_gateway

        # Check trivial case
        if not (private_site or show_age_gateway):
            return response

        # Private site not enabled and gateway passed
        if not private_site and request.COOKIES.get('age_gateway_passed'):
            return response

        # Exempted URLs
        exempted_urls = preferences.GeneralPreferences.exempted_urls        
        if exempted_urls \
            and (
                re.match(
                    r'|'.join(exempted_urls.split()), 
                    request.META['PATH_INFO']
               ) is not None
            ):
            return response

        # Exempted IP addresses
        exempted_ips = preferences.GeneralPreferences.exempted_ips
        if exempted_ips \
            and (
                re.match(
                    r'|'.join(exempted_ips.split()), 
                    request.META['REMOTE_ADDR']
               ) is not None
            ):
            return response

        # Exempted user agents. Only applicable to age gateway.
        if not private_site:
            exempted_user_agents = preferences.GeneralPreferences.exempted_user_agents
            if exempted_user_agents \
                and (
                    re.match(
                        r'|'.join(exempted_user_agents.split()), 
                        request.META['PATH_INFO']
                   ) is not None
                ):
                return response

        user = getattr(request, 'user', None)
        if (user is not None) and user.is_anonymous():
            if private_site:
                return HttpResponseRedirect(reverse('login'))
            else:
                return HttpResponseRedirect(reverse('age-gateway'))

        return response            


def get_page(self):
    """
    A function which will be monkeypatched onto the request to get the current
    integer representing the current page.
    """
    try:
        return int(self.REQUEST['page'])
    except (KeyError, ValueError, TypeError):
        return 1


class PaginationMiddleware(object):
    """Legacy middleware. It is now exactly the same as django-paginations's 
    middleware. Will be marked for deprecation soon along with get_page."""

    def process_request(self, request):
        request.__class__.page = property(get_page)
