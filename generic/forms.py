from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

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


class JoinForm(UserCreationForm):
    """Custom join form"""
    accept_terms = forms.BooleanField(required=True, label="Accept terms")

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def clean_email(self):
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']

    def __init__(self, *args, **kwargs):
        super(JoinForm, self).__init__(*args, **kwargs)

        # Adjust fields
        self.fields['email'].required = True
        self.fields['email'].help_text = _("Your email address is required in case you lose your password.")
        self.fields['username'].help_text = _("This name is visible to other users on the site.")
        self.fields['password1'].help_text = _("We never store your password in its original form.")

    def save(self, commit=True):
        # Set username to be email
        self.cleaned_data['username'] = self.cleaned_data['email']
        instance = super(JoinForm, self).save(commit=commit)
        if commit:
            instance.save()       
        return instance

