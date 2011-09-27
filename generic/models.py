from django.core.urlresolvers import reverse, Resolver404
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from preferences.models import Preferences
from ckeditor.fields import RichTextField
from snippetscream import resolve_to_name

class Link(models.Model):
    title = models.CharField(
        max_length=256,
        help_text='A short descriptive title.',
    )
    view_name = models.CharField(
        max_length=256,
        help_text="View name to which this link will redirect. This takes \
precedence over Category and URL fields below.",
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        'category.Category',
        help_text="Category to which this link will redirect. This takes \
precedence over URL field below.",
        blank=True,
        null=True,
    )
    url = models.CharField(
        max_length=256,
        help_text='URL to which this menu link will redirect.',
        blank=True,
        null=True,
    )

    def get_absolute_url(self):
        """
        Returns URL to which link should redirect based on a reversed
        view name, category or explicitly provided URL in that order
        of precedence.
        """
        if self.view_name:
            return reverse(self.view_name)
        elif self.category:
            return self.category.get_absolute_url()
        else:
            return self.url

    def is_active(self, request):
        """
        Determines whether or not the link can be consider active based on the
        request path. True if the request path can be resolved to the same view
        name as is contained in view_name field. Otherwise True if request path
        starts with URL as resolved for category contained in category field.
        Otherwise True if request path starts with URL as contained in url
        field (needs some work).
        """
        try:
            pattern_name = resolve_to_name(request.path_info)
        except Resolver404:
            pattern_name = None

        active = False
        if pattern_name:
            active = pattern_name == self.view_name
        if not active and self.category:
            active = request.path_info.startswith(self.category.get_absolute_url())
        if not active and self.url:
            active = request.path_info.startswith(self.url)
        return active

    def __unicode__(self):
        return self.title


class MenuPreferences(Preferences):
    __module__ = 'preferences.models'
    links = models.ManyToManyField(Link, through='generic.MenuLinkPosition')

    class Meta:
        verbose_name_plural = 'Menu Preferences'


class NavbarPreferences(Preferences):
    __module__ = 'preferences.models'
    links = models.ManyToManyField(Link, through='generic.NavbarLinkPosition')

    class Meta:
        verbose_name_plural = 'Navbar Preferences'


class LinkPosition(models.Model):
    link = models.ForeignKey(Link)
    position = models.IntegerField()

    class Meta():
        abstract = True
        ordering = ('position',)

    def __unicode__(self):
        return "Link titled %s in position %s." % (self.link.title, \
                self.position)


class MenuLinkPosition(LinkPosition):
    preferences = models.ForeignKey(MenuPreferences)


class NavbarLinkPosition(LinkPosition):
    preferences = models.ForeignKey(NavbarPreferences)


class GeneralPreferences(Preferences):
    __module__ = 'preferences.models'

    about_us = RichTextField()
    terms_and_conditions = RichTextField()

    class Meta:
        verbose_name_plural = 'General Preferences'

    def __unicode__(self):
        return u"General Preferences"


class RegistrationPreferences(Preferences):
    __module__ = 'preferences.models'

    raw_display_fields = models.CharField(
        'Display fields',
        max_length=32, 
        default='',
        help_text=_('Fields to display on the registration form.')
    )
    raw_required_fields = models.CharField(
        'Required fields',
        max_length=32, 
        default='',
        blank=True,
        help_text=_('Set fields which are not required by default as required on the registration form.')
    )
    raw_unique_fields = models.CharField(
        'Unique fields',
        max_length=32, 
        default='',
        blank=True,
        help_text=_('Set fields which must be unique on the registration form.')
    )

    class Meta:
        verbose_name_plural = 'Registration Preferences'

    def __unicode__(self):
        return u"Registration Preferences"

    @property
    def display_fields(self):
        return self.raw_display_fields.split(',')

    @property
    def required_fields(self):
        return self.raw_required_fields.split(',')

    @property
    def unique_fields(self):
        return self.raw_unique_fields.split(',')


class LoginPreferences(Preferences):
    __module__ = 'preferences.models'

    raw_login_fields = models.CharField(
        'Login fields',
        max_length=32, 
        default='username',
        choices=(
            ('username', _('Username only')),
            ('email', _('Email address only')),
            ('mobile', _('Mobile only')),
            ('username,email', _('Username or email address')),
        ),
        help_text=_('Users may log in with more than one identifier.')
    )

    class Meta:
        verbose_name_plural = 'Login Preferences'

    def __unicode__(self):
        return u"Login Preferences"

    @property
    def login_fields(self):
        return self.raw_login_fields.split(',')

