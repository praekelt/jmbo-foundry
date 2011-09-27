from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from preferences import preferences

class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        # Set label
        v = preferences.LoginPreferences.login_fields
        label = None
        if v == 'email':
            label = _("Email address")
        elif v == 'mobile':
            label = _("Mobile number")
        elif v == 'username,email':
            label = _("Username or email address")
        if label is not None:
            self.fields['username'].label = label

        # todo: customize error messages


class JoinForm(UserCreationForm):
    """Custom join form"""
    accept_terms = forms.BooleanField(required=True, label="Accept terms")

    class Meta:
        model = User

    def clean(self):
        cleaned_data = super(JoinForm, self).clean()

        # Validate unique fields
        required_fields = preferences.RegistrationPreferences.required_fields
        for name in required_fields:
            value = self.cleaned_data.get(name, None)
            if value is not None:
                di = {'%s__iexact' % name:value}
                if User.objects.filter(**di):
                    pretty_name = self.fields[name].label.lower()
                    message =_("The %s is already in use. Please supply a different %s." % (pretty_name, pretty_name))
                    self._errors[name] = self.error_class([message])

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(JoinForm, self).__init__(*args, **kwargs)
        
        display_fields = preferences.RegistrationPreferences.display_fields
        for name, field in self.fields.items():
            # Skip over protected fields
            if name in ('id', 'username', 'password1', 'password2', 'accept_terms'):
                continue
            if name not in display_fields:
                del self.fields[name]
            
        # Set some fields required
        required_fields = preferences.RegistrationPreferences.required_fields
        for name in required_fields:
            field = self.fields.get(name, None)
            if field and not field.required:
                field.required = True

        # Make some messages and labels more reassuring
        self.fields['username'].label = _("Display Name")
        self.fields['username'].help_text = _("This name is visible to other users on the site.")
        self.fields['password1'].help_text = _("We never store your password in its original form.")
        if self.fields.has_key('email'):
            self.fields['email'].help_text = _("Your email address is required in case you lose your password.")
