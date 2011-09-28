from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from preferences import preferences

from generic.models import Member, DefaultAvatar

def as_ul_replacement(form):
    """This formatter arranges label, widget, help text and error messages in a
    sane order. Apply to custom form classes, or use to monkey patch form
    classes not under our direct control."""
    # Yes, evil but the easiest way to set this property for all forms.
    form.required_css_class = 'required'
 
    return form._html_output(  
        normal_row = u'<li%(html_class_attr)s>%(label)s %(errors)s <div class="helptext">%(help_text)s</div> %(field)s</li>',
        error_row = u'<li>%s</li>',
        row_ender = '</li>',
        help_text_html = u'%s',
        errors_on_separate_row = False)


class TermsCheckboxInput(forms.widgets.CheckboxInput):

    def render(self, *args, **kwargs):
        result = super(TermsCheckboxInput, self).render(*args, **kwargs)
        return result + """I accept the <a href="/terms-and-conditions" target="external">terms and conditions</a>"""


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        # Set label
        v = preferences.LoginPreferences.raw_login_fields
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

    as_ul = as_ul_replacement
    
    
class JoinForm(UserCreationForm):
    """Custom join form"""
    accept_terms = forms.BooleanField(required=True, label="", widget=TermsCheckboxInput)

    class Meta:
        model = Member

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

    as_ul = as_ul_replacement


class JoinFinishForm(forms.ModelForm):
    """Show avatar selection form"""

    class Meta:
        model = Member
        fields = ('image',)

    def __init__(self, *args, **kwargs):
        super(JoinFinishForm, self).__init__(*args, **kwargs)

        self.fields['image'].label = _("Upload a picture")
        self.fields['image'].help_text = _("JPG,GIF or PNG accepted. Square is best. Keep it under 1mb.")

    @property
    def default_avatars(self):
        return DefaultAvatar.objects.all()

    def clean(self):
        cleaned_data = super(JoinFinishForm, self).clean()
        if not cleaned_data.get('image'):
            if not self.data.has_key('default_avatar_id'):
                raise forms.ValidationError(_("Please upload or select a picture."))
        return cleaned_data

    def save(self, commit=True):
        instance = super(JoinFinishForm, self).save(commit=commit)

        # Set image from default avatar if required
        if not instance.image and self.data.has_key('default_avatar_id'):
            obj = DefaultAvatar.objects.get(id=self.data['default_avatar_id'])
            instance.image = obj.image
            if commit:
                instance.save()

        return instance

    as_ul = as_ul_replacement

