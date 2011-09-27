import inspect

from django.core.urlresolvers import reverse, Resolver404
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor.fields import RichTextField
from preferences.models import Preferences
from snippetscream import resolve_to_name

from generic.templatetags import element_styles

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


class LoginRegistrationPreferences(Preferences):
    __module__ = 'preferences.models'

    login_fields = models.CharField(
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
        verbose_name_plural = 'Login and Registration Preferences'

    def __unicode__(self):
        return u"Login and registration Preferences"


class ElementPreferences(Preferences):
    __module__ = 'preferences.models'
    
    class Meta:
        verbose_name_plural = 'Element preferences'

class ElementOption(models.Model):
    preferences = models.ForeignKey('preferences.ElementPreferences')
    title = models.CharField(
        max_length=256,
        help_text='A short descriptive title.',
    )
    content = models.ManyToManyField(
        'jmbo.ModelBase',
        help_text="Content to display, takes preference over Category field.",
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        'category.Category',
        help_text="Category for which to collect objects.",
        blank=True,
        null=True,
    )
    count = models.IntegerField(
        help_text="Number of content objects to display.",
    )
    style = models.CharField(
        choices=((style[0], style[0]) for style in inspect.getmembers(element_styles, inspect.isclass)),
        max_length=64
    )
    position = models.IntegerField()
