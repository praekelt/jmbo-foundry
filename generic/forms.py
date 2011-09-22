from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from preferences import preferences

class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        # Set label
        v = preferences.LoginRegistrationPreferences.login_fields
        label = None
        if v == 'email':
            label = _("Email address")
        elif v == 'mobile':
            label = _("Mobile number")
        elif v == 'username_or_email':
            label = _("Username or email address")
        if label is not None:
            self.fields['username'].label = label

        # todo: customize error messages
