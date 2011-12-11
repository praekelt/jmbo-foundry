import inspect

from django.core.urlresolvers import reverse, Resolver404
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.comments.models import Comment as BaseComment

from ckeditor.fields import RichTextField
from preferences.models import Preferences
from snippetscream import resolve_to_name
from photologue.models import ImageModel
from jmbo.utils import generate_slug

from foundry.profile_models import AbstractAvatarProfile, \
    AbstractSocialProfile, AbstractContactProfile
from foundry.templatetags import listing_styles
import foundry.monkey


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
        help_text='URL to which this link will redirect.',
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


class Menu(models.Model):
    """A tile menu contains ordered links"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
        unique=True,
    )
    display_title = models.BooleanField(default=True)

    def __unicode__(self):
        return self.title


class Navbar(models.Model):
    """A tile navbar contains ordered links"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
        unique=True,
    )

    def __unicode__(self):
        return self.title


class Listing(models.Model):
    """A themed, ordered collection of items"""
    title = models.CharField(
        max_length=256,
        help_text='A short descriptive title.',
    )
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
        unique=True,
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
        choices=((style[0], style[0]) for style in inspect.getmembers(listing_styles, inspect.isclass) if style[0] != 'AbstractBaseStyle'),
        max_length=64
    )
    display_likes = models.BooleanField(default=True)

    def __unicode__(self):
        return self.title


class AbstractLinkPosition(models.Model):
    link = models.ForeignKey(Link)
    position = models.IntegerField()
    condition_expression = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='A python expression. Variable request is in scope.'
    )

    class Meta():
        abstract = True
        ordering = ('position',)

    def __unicode__(self):
        return "Link titled %s in position %s." % (self.link.title, \
                self.position)

    def condition_expression_result(self, request):
        if not self.condition_expression:
            return True
        return eval(self.condition_expression)


class MenuLinkPosition(AbstractLinkPosition):
    menu = models.ForeignKey(Menu)


class NavbarLinkPosition(AbstractLinkPosition):
    navbar = models.ForeignKey(Navbar)


class GeneralPreferences(Preferences):
    __module__ = 'preferences.models'

    about_us = RichTextField()
    terms_and_conditions = RichTextField()
    privacy_policy = RichTextField()
    private_site = models.BooleanField(
        default=False,
        help_text=_("A private site requires a visitor to be logged in to view any content."),
    )
    show_age_gateway = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'General Preferences'


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

    @property
    def display_fields(self):
        return [s for s in self.raw_display_fields.split(',') if s]

    @property
    def required_fields(self):
        return [s for s in self.raw_required_fields.split(',') if s]

    @property
    def unique_fields(self):
        return [s for s in self.raw_unique_fields.split(',') if s]

    def save(self, *args, **kwargs):
        # Unique fields must be unique! Check the existing members for possible
        # duplicate values. For example, if mobile number was not a unique
        # field before but it is now, then there may not be two members with
        # the same mobile number.
        for fieldname in self.unique_fields:
            values = Member.objects.all().values_list(fieldname, flat=True)
            # set removes duplicates from a list
            if len(values) != len(set(values)):
                raise RuntimeError(
                    "Cannot set %s to be unique since there is more than one \
                        member with the same %s." % (fieldname, fieldname)
                )
        super(RegistrationPreferences, self).save(*args, **kwargs)


class LoginPreferences(Preferences):
    __module__ = 'preferences.models'

    raw_login_fields = models.CharField(
        'Login fields',
        max_length=32, 
        default='username',
        choices=(
            ('username', _('Username only')),
            ('email', _('Email address only')),
            ('mobile_number', _('Mobile number only')),
            ('username,email', _('Username or email address')),
            ('username,mobile_number', _('Username or mobile number')),
        ),
        help_text=_('Users may log in with more than one identifier.')
    )

    class Meta:
        verbose_name_plural = 'Login Preferences'

    @property
    def login_fields(self):
        return self.raw_login_fields.split(',')


class PasswordResetPreferences(Preferences):
    __module__ = 'preferences.models'

    lookup_field = models.CharField(
        max_length=32, 
        default='email',
        choices=(
            ('email', _('Email address')),
            ('mobile_number', _('Mobile number')),
        ),
        help_text=_('The field a user must enter to retrieve his password.')
    )

    class Meta:
        verbose_name_plural = 'Password Reset Preferences'


class Member(User, AbstractAvatarProfile, AbstractSocialProfile, AbstractContactProfile):
    """Class that models the default user account. Subclassing is superior to profiles since 
    a site may conceivably have more than one type of user account, but the profile architecture 
    limits the entire site to a single type of profile."""
    
    def __unicode__(self):
        return self.username


class DefaultAvatar(ImageModel):
    """A set of avatars users can choose from"""
    pass


class Country(models.Model):
    """Countries used in the age gateway"""
    title = models.CharField(max_length=32)
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
        unique=True,
    )
    minimum_age = models.PositiveIntegerField(default=18)

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('title',)

    def __unicode__(self):
        return self.title


class Page(models.Model):
    title = models.CharField(
        max_length=200, help_text='A title that may appear in the browser window caption.',
    )
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
        unique=True,
    )
    is_homepage = models.BooleanField(default=False, help_text="Tick if you want this page to be the site's homepage.")
    sites = models.ManyToManyField(
        'sites.Site',
        blank=True,
        null=True,
        help_text='Sites that this page will appear on.',
    )

    def __unicode__(self):
        return self.title

    @property
    def rows(self):
        return self.row_set.all().order_by('index')

    @property
    def rows_by_block_name(self):
        """Return rows grouped by block_name."""
        result = {}
        for row in self.rows:
            result.setdefault(row.block_name, [])
            result[row.block_name].append(row)
        return result

    @property
    def render_height(self):
        return sum([o.render_height+20 for o in self.rows])


class Row(models.Model):
    page = models.ForeignKey(Page)
    index = models.PositiveIntegerField(default=0, editable=False)
    block_name = models.CharField(
        max_length=32, 
        default='content',
        choices=(
            ('header', _('Header')),
            ('content', _('Content')),
            ('footer', _('Footer')),
        ),        
        help_text="The Django base template block that this row is rendered \
            within. It is only applicable if the page is set to be the home \
            page."
    )

    def save(self, *args, **kwargs):        
        if not self.id:
            self.index = self.page.row_set.count()
        super(Row, self).save(*args, **kwargs)

    @property
    def columns(self):
        return self.column_set.all().order_by('index')

    @property
    def render_height(self):
        return max([o.render_height+8 for o in self.columns] + [0]) + 44


class Column(models.Model):
    row = models.ForeignKey(Row)
    index = models.PositiveIntegerField(default=0, editable=False)
    width = models.PositiveIntegerField(default=8)    

    def save(self, *args, **kwargs):        
        if not self.id:
            self.index = self.row.column_set.count()
        super(Column, self).save(*args, **kwargs)

    @property
    def tiles(self):
        return self.tile_set.all().order_by('index')

    @property
    def render_width(self):
        """Take border into account"""
        return self.width * 60 - 2

    @property
    def render_height(self):
        return sum([o.render_height+8 for o in self.tiles]) + 44


class Tile(models.Model):
    column = models.ForeignKey(Column)
    index = models.PositiveIntegerField(default=0, editable=False)

    target_content_type = models.ForeignKey(ContentType, null=True, related_name='tile_target_content_type')
    target_object_id = models.PositiveIntegerField(null=True)
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')

    view_name = models.CharField(
        max_length=200, 
        null=True,
        blank=True,
        help_text="""A view to be rendered in this tile. This view is \
typically a snippet of a larger page. If you are unsure test and see if \
it works - you cannot break anything.""",
    )
    class_name = models.CharField(
        max_length=200, null=True, blank=True,
        help_text="One or more CSS classes that are applied to the tile.",
    )
    enable_ajax = models.BooleanField(default=False)
    condition_expression = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='A python expression. Variable request is in scope.'
    )

    def save(self, *args, **kwargs):        
        if not self.id:
            self.index = self.column.tile_set.count()
        super(Tile, self).save(*args, **kwargs)

    @property
    def render_height(self):
        return 60

    @property
    def label(self):
        return str(self.target or self.view_name)

    def condition_expression_result(self, request):
        if not self.condition_expression:
            return True
        return eval(self.condition_expression)


class FoundryComment(BaseComment):
    """Custom comment class"""
    in_reply_to = models.ForeignKey('self', null=True, blank=True, db_index=True)

    @property
    def replies(self):
        return FoundryComment.objects.filter(in_reply_to=self).order_by('id')

    '''
    def can_vote(self, request):
        """Play along with Panya API"""
        return True, 'can_vote'

    def likes_enabled(self):
        """Play along with Panya API"""
        return True

    @property
    def as_leaf_class(self):
        """Play along with Panya API"""
        return {'content_type':'foundrycomment'}
    '''        

    @property
    def creator(self):
        return User.objects.get(id=self.user_id)
