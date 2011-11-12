from django.conf import settings


def _build_view_names_recurse(url_patterns=None):
    """
    Returns a tuple of url pattern names suitable for use as field choices
    """
    if not url_patterns:
        urlconf = settings.ROOT_URLCONF
        url_patterns = __import__(settings.ROOT_URLCONF, globals(), locals(), \
                ['urlpatterns', ], -1).urlpatterns

    result = []
    for pattern in url_patterns:
        try:
            #result.append((pattern.name, pattern.name.title().replace('_', \
            #        ' ')))
            if pattern.name is not None:
                result.append((pattern.name, pattern.name))
        except AttributeError:
            # If the pattern itself is an include, recurively fetch it
            # patterns. Ignore admin patterns.
            if not pattern.regex.pattern.startswith('^admin'):
                try:
                    result += _build_view_names_recurse(pattern.url_patterns)
                except AttributeError:
                    pass
    return result


def get_view_choices():
    result = _build_view_names_recurse()
    result.sort()
    return result

