from django.conf import settings


_foundry_utils_cache = {}

def _build_view_names_recurse(url_patterns=None):
    """
    Returns a tuple of url pattern names suitable for use as field choices
    """
    if url_patterns is None:
        urlconf = settings.ROOT_URLCONF
        url_patterns = __import__(settings.ROOT_URLCONF, globals(), locals(), \
                ['urlpatterns', ], -1).urlpatterns

    result = []
    for pattern in url_patterns:
        try:
            # Rules: (1) named patterns (2) may not contain arguments.
            if pattern.name is not None:
                if pattern.regex.pattern.find('<') == -1:
                    result.append((pattern.name, pattern.name))
        except AttributeError:
            # If the pattern itself is an include, recursively fetch its
            # patterns. Ignore admin patterns.
            if not pattern.regex.pattern.startswith('^admin'):
                try:
                    result += _build_view_names_recurse(pattern.url_patterns)
                except AttributeError:
                    pass
    return result


def get_view_choices():
    # Implement a simple module level cache. The result never changes 
    # for the duration of the Django process life.
    if not _foundry_utils_cache.has_key('get_view_choices'):
        result = _build_view_names_recurse()
        result.sort()
        _foundry_utils_cache['get_view_choices'] = result
    return _foundry_utils_cache['get_view_choices']
