import re

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

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
            '/password_reset', '/static'
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
