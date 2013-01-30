from django.conf import settings


_foundry_utils_cache = {}

def _build_view_names_recurse(url_patterns=None, simple=True):
    """
    Returns a tuple of url pattern names suitable for use as field choices
    """
    if url_patterns is None:
        urlconf = settings.ROOT_URLCONF
        url_patterns = __import__(
            settings.ROOT_URLCONF, globals(), locals(), ['urlpatterns', ], -1
        ).urlpatterns

    result = []
    for pattern in url_patterns:
        try:
            # Include only named patterns
            # Rules: (1) named patterns (2) may not contain arguments.
            if pattern.name is not None:
                if simple:
                    # May not contain arguments
                    if pattern.regex.pattern.find('<') == -1:
                        result.append((pattern.name, pattern.name))                           
                else:
                    result.append((pattern.name, pattern.name))
        except AttributeError:
            # If the pattern itself is an include, recursively fetch its
            # patterns. Ignore admin patterns.
            if not pattern.regex.pattern.startswith('^admin'):
                try:
                    result += _build_view_names_recurse(
                        pattern.url_patterns, simple
                    )
                except AttributeError:
                    pass
    return result


def get_view_choices(simple=True):
    # Implement a simple module level cache. The result never changes 
    # for the duration of the Django process life.
    key = 'get_view_choices_%s' % (simple and 1 or 0)
    if not _foundry_utils_cache.has_key(key):
        result = _build_view_names_recurse(simple=simple)
        result.sort()
        _foundry_utils_cache[key] = result
    return _foundry_utils_cache[key]
