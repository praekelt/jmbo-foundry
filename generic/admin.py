from django import forms
from django.contrib import admin

from generic.models import Link, MenuLinkPosition, MenuPreferences, \
        NavbarLinkPosition, NavbarPreferences

from preferences.admin import PreferencesAdmin

from django.conf import settings


def build_view_names(url_patterns=None):
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
            result.append((pattern.name, pattern.name.title().replace('_', \
                    ' ')))
        except AttributeError:
            # If the pattern itself is an include, recurively fetch it
            # patterns. Ignore admin patterns.
            if not pattern.regex.pattern.startswith('^admin'):
                try:
                    result += build_view_names(pattern.url_patterns)
                except AttributeError:
                    pass
    return result


class LinkAdminForm(forms.ModelForm):
    view_name = forms.ChoiceField(
        label='View Name',
        help_text="View name to which this link will redirect. This takes \
precedence over url field below.",
        required=False
    )

    class Meta:
        model = Link

    def __init__(self, *args, **kwargs):
        """
        Set view_name choices to url pattern names
        """
        self.declared_fields['view_name'].choices = [('', '---------'), ] + \
                build_view_names()

        super(LinkAdminForm, self).__init__(*args, **kwargs)


class MenuLinkPositionInline(admin.StackedInline):
    model = MenuLinkPosition


class NavbarLinkPositionInline(admin.StackedInline):
    model = NavbarLinkPosition


class MenuPreferenceAdmin(PreferencesAdmin):
    inlines = [
        MenuLinkPositionInline,
    ]


class NavbarPreferenceAdmin(PreferencesAdmin):
    inlines = [
        NavbarLinkPositionInline,
    ]


class LinkAdmin(admin.ModelAdmin):
    form = LinkAdminForm


admin.site.register(MenuPreferences, MenuPreferenceAdmin)
admin.site.register(NavbarPreferences, NavbarPreferenceAdmin)
admin.site.register(Link, LinkAdmin)
