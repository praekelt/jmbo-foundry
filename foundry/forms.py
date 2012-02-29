import datetime
import re

from django.utils.translation import ugettext_lazy as _, ugettext
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    PasswordResetForm as BasePasswordResetForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import Context, loader
from django.utils.http import int_to_base36
from django.http import HttpResponseRedirect
from django.contrib.comments.forms import CommentForm as BaseCommentForm
from django.contrib.sites.models import Site
from django.conf import settings

from preferences import preferences
from jmbo.forms import as_div

from foundry.models import Member, DefaultAvatar, Country, FoundryComment, \
    BlogPost, MemberFriend
from foundry.widgets import OldSchoolDateWidget
from foundry.ambientmobile import AmbientSMS, AmbientSMSError


class TermsCheckboxInput(forms.widgets.CheckboxInput):

    def render(self, *args, **kwargs):
        result = super(TermsCheckboxInput, self).render(*args, **kwargs)
        return result + ugettext("""I accept the <a href="/terms-and-conditions" target="external">terms and conditions</a>""")


class RememberMeCheckboxInput(forms.widgets.CheckboxInput):

    def render(self, *args, **kwargs):
        result = super(RememberMeCheckboxInput, self).render(*args, **kwargs)
        return result + "Remember me"


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        # Set label
        v = preferences.LoginPreferences.raw_login_fields
        label = None
        if v == 'email':
            label = _("Email address")
        elif v == 'mobile_number':
            label = _("Mobile number")
        elif v == 'username,email':
            label = _("Username or email address")
        elif v == 'username,mobile_number':
            label = _("Username or mobile number")
        if label is not None:
            self.fields['username'].label = label

        # todo: customize error messages

    as_div = as_div
    
    
class JoinForm(UserCreationForm):
    """Custom join form"""
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    date_of_birth = forms.DateField(widget=OldSchoolDateWidget) # todo: widget
    accept_terms = forms.BooleanField(required=True, label="", widget=TermsCheckboxInput)

    class Meta:
        model = Member

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data["mobile_number"]
        if not re.match(r'[\+]?[0-9]*$', mobile_number):
            raise forms.ValidationError(_("Please enter a valid number"))
        return mobile_number

    def clean(self):
        cleaned_data = super(JoinForm, self).clean()

        # Validate unique fields
        required_fields = preferences.RegistrationPreferences.required_fields
        for name in required_fields:
            value = self.cleaned_data.get(name, None)
            if value is not None:
                di = {'%s__iexact' % name:value}
                if Member.objects.filter(**di).count() > 0:
                    pretty_name = self.fields[name].label.lower()
                    message =_("The %(pretty_name)s is already in use. \
Please supply a different %(pretty_name)s." % {'pretty_name': pretty_name}
                    )
                    self._errors[name] = self.error_class([message])

        # Age gateway fields
        if self.show_age_gateway:
            country = cleaned_data.get('country')
            date_of_birth = cleaned_data.get('date_of_birth')
            if country and date_of_birth:
                today = datetime.date.today()
                if date_of_birth > today.replace(today.year - country.minimum_age):
                    msg = "You must be at least %s years of age to use this site." \
                        % country.minimum_age
                    raise forms.ValidationError(_(msg))

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.show_age_gateway = kwargs.pop('show_age_gateway')
        super(JoinForm, self).__init__(*args, **kwargs)
        
        display_fields = preferences.RegistrationPreferences.display_fields
        if self.show_age_gateway:
            display_fields += ['country', 'date_of_birth']
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

        # Remove accept_terms if terms and conditions not set
        if not preferences.GeneralPreferences.terms_and_conditions:
            del self.fields['accept_terms']

        # Make some messages and labels more reassuring
        self.fields['username'].help_text = _("This name is visible to other users on the site.")
        self.fields['password1'].help_text = _("We never store your password in its original form.")
        if self.fields.has_key('email'):
            self.fields['email'].help_text = _("Your email address is required in case you lose your password.")
        if self.fields.has_key('mobile_number'):
            # There is somebug in Django that does not allow translation to be
            # applied. Workaround.
            self.fields['mobile_number'].label = _("Mobile number")
            self.fields['mobile_number'].help_text = _("The number must be in \
international format and may start with a + sign. All other characters must \
be numbers. No spaces allowed. An example is +27821234567.")

    as_div = as_div


class JoinFinishForm(forms.ModelForm):
    """Show avatar selection form"""

    class Meta:
        model = Member
        fields = ('image',)

    def __init__(self, *args, **kwargs):
        super(JoinFinishForm, self).__init__(*args, **kwargs)

        self.fields['image'].label = _("Upload a picture")
        self.fields['image'].help_text = _("JPG, GIF or PNG accepted. Square is best. Keep it under 1MB.")

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

    as_div = as_div


class PasswordResetForm(BasePasswordResetForm):
    """Custom form since we do not necessarily want to lookup the email
    address"""
    mobile_number = forms.CharField(label=_("Mobile number"))

    def clean_mobile_number(self):
        """Clean method must have the same structure as clean_email in
        BasePasswordResetForm"""
        mobile_number = self.cleaned_data["mobile_number"]
        self.users_cache = Member.objects.filter(
            mobile_number__iexact=mobile_number,
            is_active=True
        )
        if self.users_cache.count() == 0:
            raise forms.ValidationError(_("The mobile number is not registered with the system."))
        return mobile_number

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

        v = preferences.PasswordResetPreferences.lookup_field
        if v == 'email':
            del self.fields['mobile_number']
        else:
            del self.fields['email']
        
    def save(self, domain_override=None, email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator, from_email=None, request=None):
        """Override entire method. Due to the layout of the original method we
        cannot do a super() call."""
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            t = loader.get_template(email_template_name)
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            content = t.render(Context(c))
            if self.fields.has_key('email'):
                send_mail(
                    _("Password reset on %s") % site_name, 
                    content, from_email, [user.email]
                )
            else:
                sms = AmbientSMS(
                    settings.FOUNDRY['sms_gateway_api_key'], 
                    settings.FOUNDRY['sms_gateway_password']
                )
                try:
                    sms.sendmsg(content, [self.cleaned_data['mobile_number']])
                except AmbientSMSError:
                    pass

    as_div = as_div


class AgeGatewayForm(forms.Form):
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    date_of_birth = forms.DateField(widget=OldSchoolDateWidget)
    remember_me = forms.BooleanField(required=False, label="", widget=RememberMeCheckboxInput)

    def clean(self):
        cleaned_data = super(AgeGatewayForm, self).clean()

        country = cleaned_data.get('country')
        date_of_birth = cleaned_data.get('date_of_birth')
        if country and date_of_birth:
            today = datetime.date.today()
            if date_of_birth > today.replace(today.year - country.minimum_age):
                msg = "You must be at least %s years of age to use this site." \
                    % country.minimum_age
                raise forms.ValidationError(_(msg))

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(AgeGatewayForm, self).__init__(*args, **kwargs)

        self.fields['country'].label = _("Where do you live?")

    def save(self, request):
        """Set cookie"""
        expires = None
        if self.cleaned_data['remember_me']:            
            now = datetime.datetime.now()
            expires = now.replace(year=now.year+10)
        response = HttpResponseRedirect('/')        
        response.set_cookie('age_gateway_passed', value=1, expires=expires)
        return response

    as_div = as_div


class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=64)

    as_div = as_div


class CommentForm(BaseCommentForm):
    in_reply_to = forms.CharField(max_length=10, required=False, widget=forms.widgets.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget = forms.widgets.HiddenInput()
        self.fields['email'].widget = forms.widgets.HiddenInput()
        self.fields['url'].widget = forms.widgets.HiddenInput()

        # Set to anonymous values since we do not have either the request or a
        # user object to use at this stage. We don't care about these values 
        # if user is set on a comment object.
        self.fields['name'].initial = 'Anonymous'
        self.fields['email'].initial = 'anonymous@jmbo.org'

    def get_comment_model(self):
        return FoundryComment

    def get_comment_create_data(self):
        data = super(CommentForm, self).get_comment_create_data()
        data['in_reply_to_id'] = self.cleaned_data['in_reply_to']
        return data


class CreateBlogPostForm(forms.ModelForm):

    class Meta:
        model = BlogPost
        fields = ('title', 'content')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.site = kwargs.pop('site')
        super(CreateBlogPostForm, self).__init__(*args, **kwargs)
        # There is some bug in Django that does not allow translation to be
        # applied. Workaround.
        self.fields['content'].label = _("Content")

    def save(self, commit=True):    
        instance = super(CreateBlogPostForm, self).save(commit=commit)
        # Set owner, publish to current site
        instance.owner = self.user
        instance.sites = [self.site]
        instance.state = 'published'
        if commit:
            instance.save()
        return instance            

    as_div = as_div


class FriendRequestForm(forms.ModelForm):
    """This form does not follow the usual style since we do not want any 
    fields to render."""

    class Meta:
        model = MemberFriend
        fields = []

    def __init__(self, *args, **kwargs):
        super(FriendRequestForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(FriendRequestForm, self).clean()
        member = self.initial['member']
        friend = self.initial['friend']
        q = MemberFriend.objects.filter(member=member, friend=friend)
        if q.filter(state='invited').exists():
            raise forms.ValidationError(
                _("You have already sent a friend request to %s" % friend.username)
            )
        if q.filter(state='accepted').exists():
            raise forms.ValidationError(
                _("You are already friends with %s" % friend.username)
            )
        if q.filter(state='declined').exists():
            raise forms.ValidationError(
                _("You may not be friends with %s" % friend.username)
            )
        cleaned_data['member'] = member
        cleaned_data['friend'] = friend
        cleaned_data['state'] = 'accepted'
        return cleaned_data

    def save(self, commit=True):
        self._meta.fields = ('member', 'friend', 'state')
        instance = super(FriendRequestForm, self).save(commit=commit)
        return instance

    as_div = as_div


# Form for testing
class TestForm(forms.Form):
    title = forms.CharField(max_length=20)

    as_div = as_div


# Monkey patch some methods. Cannot put in monkey.py due to circular imports.
from contact.forms import SiteContactForm

SiteContactForm.as_p = as_div
