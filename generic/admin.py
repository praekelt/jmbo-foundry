from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings

from preferences.admin import PreferencesAdmin

from generic.models import ElementOption, ElementPreferences, Link, \
        MenuLinkPosition, MenuPreferences, NavbarLinkPosition, \
        NavbarPreferences, GeneralPreferences, GeneralPreferences, \
        RegistrationPreferences, LoginPreferences
from generic.widgets import SelectCommaWidget

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


class GeneralPreferencesAdmin(PreferencesAdmin):
    pass


class RegistrationPreferencesAdminForm(forms.ModelForm):
    """Form enabling the use of MultipleChoiceCommaField"""

    class Meta:
        model = RegistrationPreferences
        widgets = {
            'raw_display_fields':SelectCommaWidget,
            'raw_required_fields':SelectCommaWidget,
            'raw_unique_fields':SelectCommaWidget
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationPreferencesAdminForm, self).__init__(*args, **kwargs)
        protected_fields = ('id', 'username', 'password')
        choices = [(unicode(f.name), f.name) for f in User._meta.fields if f.name not in protected_fields]
        self.fields['raw_display_fields'].widget.choices = choices
        self.fields['raw_unique_fields'].widget.choices = choices
        choices = [(f.name, f.name) for f in User._meta.fields if f.blank and (f.name not in protected_fields)]
        self.fields['raw_required_fields'].widget.choices = choices

class RegistrationPreferencesAdmin(PreferencesAdmin):
    form = RegistrationPreferencesAdminForm


class LoginPreferencesAdmin(PreferencesAdmin):
    pass

class ElementOptionInline(admin.StackedInline):
    model = ElementOption

class ElementPreferencesAdmin(PreferencesAdmin):
    inlines = [
        ElementOptionInline,
    ]

admin.site.register(MenuPreferences, MenuPreferenceAdmin)
admin.site.register(NavbarPreferences, NavbarPreferenceAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(GeneralPreferences, GeneralPreferencesAdmin)
admin.site.register(ElementPreferences, ElementPreferencesAdmin)
admin.site.register(RegistrationPreferences, RegistrationPreferencesAdmin)
admin.site.register(LoginPreferences, LoginPreferencesAdmin)


