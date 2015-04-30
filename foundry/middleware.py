import re
import jwt
from datetime import datetime
from calendar import timegm
from urlparse import urlparse

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.utils import timezone

from foundry.models import Member, Country
from foundry.utils import get_preference, get_age


PROTECTED_URLS_PATTERN = None
AG_TOKEN_MAX_TIME_TO_EXPIRY = 60  # in seconds
AG_TOKEN_PARAMETER_NAME = 't_ag'


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
        global PROTECTED_URLS_PATTERN
        if not PROTECTED_URLS_PATTERN:
            PROTECTED_URLS_PATTERN = r'|'.join((
                reverse('age-gateway'),
                reverse('join'),
                reverse('login'),
                reverse('logout'),
                reverse('password_reset'),
                reverse('terms-and-conditions'),
                '/auth/password_reset/',
                '/static/',
                '/admin/',
            ))
        if re.match(PROTECTED_URLS_PATTERN, request.META['PATH_INFO']) is not None:
            return response

        # Listing feeds also exempted
        # todo: make the test more refined.
        if request.META['PATH_INFO'].endswith('/feed/'):
            return response

        # Now only do we possibly hit the database
        private_site = get_preference('GeneralPreferences', 'private_site')
        show_age_gateway = get_preference('GeneralPreferences', 'show_age_gateway')

        # Check trivial case
        if not (private_site or show_age_gateway):
            return response

        # Private site not enabled and gateway passed
        if not private_site and request.COOKIES.get('age_gateway_passed'):
            return response

        # Exempted URLs
        exempted_urls = get_preference('GeneralPreferences', 'exempted_urls')
        if exempted_urls \
            and (
                re.match(
                    r'|'.join(exempted_urls.split()),
                    request.META['PATH_INFO']
               ) is not None
            ):
            return response

        # Exempted IP addresses
        exempted_ips = get_preference('GeneralPreferences', 'exempted_ips')
        if exempted_ips \
            and (
                re.match(
                    r'|'.join(exempted_ips.split()),
                    request.META['REMOTE_ADDR']
               ) is not None
            ):
            return response

        # Exempted user agents
        exempted_user_agents = get_preference('GeneralPreferences', 'exempted_user_agents')
        if exempted_user_agents \
            and (
                re.match(
                    r'|'.join(exempted_user_agents.split()),
                    request.META.get('HTTP_USER_AGENT', '')
               ) is not None
            ):
            return response

        user = getattr(request, 'user', None)
        if (user is not None) and user.is_anonymous():
            if private_site:
                return redirect_to_login(request.path_info,
                                         login_url=reverse('login'))
            else:
                # check if a partner site has supplied this
                # site with the user's age
                ag_values, expires = self.get_partner_age_gateway_values(request)
                if ag_values and expires:
                    # verify age and automatically pass age gateway
                    dob = datetime.strptime(ag_values[3:], '%d-%m-%Y').date()
                    if Country.objects.filter(country_code__iexact=ag_values[:2],
                                              minimum_age__lte=get_age(dob)).exists():
                        response.set_cookie('age_gateway_passed', value=1,
                                            expires=expires)
                        response.set_cookie('age_gateway_values', value=ag_values,
                                            expires=expires)
                        return response
                return redirect_to_login(request.path_info,
                                         login_url=reverse('age-gateway'))

        return response

    def get_partner_age_gateway_values(self, request):
        """
        Checks if age gateway values have been supplied by a partner site in a
        JWT token. Returns (ag_values, expires) if valid, otherwise (None, None).
        The token is only valid if
        1. the payload expiry time is not yet past (field 'exp'),
        2. the time to payload expiry is less than AG_TOKEN_MAX_TIME_TO_EXPIRY,
        3. both the 'e' (cookie expiry) and 'v' (cookie value) fields are supplied,
        4. HTTP_REFERER matches a partner site.
        """
        if AG_TOKEN_PARAMETER_NAME in request.GET:
            token = request.GET[AG_TOKEN_PARAMETER_NAME]
            ref_domain = urlparse(request.META.get('HTTP_REFERER', '')).netloc
            partner_config = get_preference('GeneralPreferences',
                                            'partner_site_configuration')

            try:
                # get domains and JWT keys - will raise ValueError
                # if the partner_site_configuration format is incorrect
                domain_key_map = dict(line.split(' ', 1) for line in
                                      partner_config.strip('\n').split('\n'))
                # raises KeyError if referer is not a partner domain
                jwt_shared_secret = domain_key_map[ref_domain]

                payload = jwt.decode(token, jwt_shared_secret)
                from_expiry = (timegm(datetime.utcnow().utctimetuple())
                               - int(payload['exp']))

                # make sure a partner site cannot set a token
                # that expires too far in the future
                if from_expiry > AG_TOKEN_MAX_TIME_TO_EXPIRY:
                    raise jwt.ExpiredSignature

                if len(payload['v']) != 13:
                    raise ValueError

                # assume UTC timestamp
                return (payload['v'], datetime.strptime(payload['e'],
                                                        '%Y-%m-%dT%H:%M:%S'))

            except (jwt.DecodeError, jwt.ExpiredSignature,
                    KeyError, ValueError):
                pass

        return None, None


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


class CheckProfileCompleteness:
    """If user has any outstanding required fields then redirect. Must run
    after AuthenticationMiddleware."""

    def process_response(self, request, response):

        if request.META['PATH_INFO'] == reverse('complete-profile'):
            return response

        # This check is only really required when running in debug mode
        if request.META['PATH_INFO'].startswith(settings.MEDIA_URL):
            return response

        # Ignore ajax
        if request.is_ajax():
            return response

        user = getattr(request, 'user', None)
        if isinstance(user, Member) and not user.is_profile_complete:
            return HttpResponseRedirect(reverse('complete-profile'))

        return response


class LastSeen:
    """Update a user's last seen field at most every 5 minutes."""

    def process_response(self, request, response):

        # Update last_seen if the cookie has expired and this is an authenticated member
        user = getattr(request, 'user', None)
        if isinstance(user, Member) and not request.COOKIES.get('last_seen', None):
            user.last_seen = timezone.now()
            user.save()
            response.set_cookie('last_seen', '1', max_age=300)

        return response
