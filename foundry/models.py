import inspect
import re
import cPickle

from django.core.cache import cache
from django.core.urlresolvers import reverse, Resolver404, NoReverseMatch
from django.db import models
from django.db.models import Q
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, UserManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.comments.models import Comment as BaseComment
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.importlib import import_module
from django.utils import simplejson as json
from django.conf import settings

from ckeditor.fields import RichTextField
from preferences.models import Preferences
from preferences import preferences
from snippetscream import resolve_to_name
from photologue.models import ImageModel
from south.modelsinspector import add_introspection_rules
from zope.interface import implements

from jmbo.models import ModelBase
from jmbo.managers import DefaultManager
from foundry.profile_models import AbstractAvatarProfile, \
    AbstractSocialProfile, AbstractPersonalProfile, \
    AbstractContactProfile, AbstractSubscriptionProfile, \
    AbstractLocationProfile
from foundry.templatetags.listing_styles import LISTING_CLASSES
from foundry.managers import PermittedManager
from foundry.interfaces import ITileProvider
from foundry.mixins import CachingMixin
from foundry.utils import get_view_choices
import foundry.monkey

# regex that identifies scripts in text
SCRIPT_REGEX = re.compile(r"""(<script[^>]*>)|(<[^>]* on[a-z]+=['"].*?['"][^>]*)""", flags=re.DOTALL)


class AttributeWrapper:
    """Wrapper that allows attributes to be added or overridden on an object"""

    def __init__(self, obj, **kwargs):
        self._obj = obj
        self._attributes = {}
        for k, v in kwargs.items():
            self._attributes[k] = v

    def __getattr__(self, key):
        if key in self._attributes:
            return self._attributes[key]
        return getattr(self._obj, key)

    def __setstate__(self, dict):
        self.__dict__.update(dict)

    @property
    def klass(self):
        """Can't override __class__ and making it a property also does not
        work. Could be because of Django metaclasses."""
        return self._obj.__class__


class Link(models.Model):
    title = models.CharField(
        max_length=256,
        help_text='A short descriptive title.',
    )
    subtitle = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text='Some titles may be the same. A subtitle makes a distinction. It is not displayed on the site.',
    )
    view_name = models.CharField(
        max_length=256,
        help_text="View name to which this link will redirect.",
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        'category.Category',
        help_text="Category to which this link will redirect.",
        blank=True,
        null=True,
    )
    target_content_type = models.ForeignKey(
        ContentType, blank=True, null=True, related_name='link_target_content_type'
    )
    target_object_id = models.PositiveIntegerField(blank=True, null=True)
    target = generic.GenericForeignKey(
        'target_content_type', 'target_object_id'
    )
    url = models.CharField(
        max_length=256,
        help_text='URL to which this link will redirect.',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('title', 'subtitle')

    def __unicode__(self):
        if self.subtitle:
            return '%s (%s)' % (self.title, self.subtitle)
        else:
            return self.title

    def get_absolute_url(self):
        """Returns URL to which link should redirect based on a reversed view
        name, category, target or explicitly provided URL."""
        if self.view_name:
            return reverse(self.view_name)
        elif self.category:
            return self.category.get_absolute_url()
        elif self.target:
            return self.target.get_absolute_url()
        else:
            # Django can be served in a subdirectory. Transparently fix urls.
            if '://' in self.url:
                return self.url

            # Urls not starting with a slash proably do so with reason. Skip.
            if not self.url.startswith('/'):
                return self.url

            # Request is not available here so use reverse to determine root
            try:
                root = reverse('home')
            except NoReverseMatch:
                return self.url

            # /abc and /today/abc must be transformed into /today/abc
            if not self.url.startswith(root):
                return root.rstrip('/') + '/' + self.url.lstrip('/')

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
        if not active and self.target:
            active = request.path_info.startswith(self.target.get_absolute_url())
        if not active and self.url:
            active = request.path_info.startswith(self.url)
        return active


class Menu(CachingMixin):
    """A tile menu contains ordered links"""
    title = models.CharField(max_length=255)
    subtitle = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text='Some titles may be the same. A subtitle makes a distinction. It is not displayed on the site.',
    )
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
    )
    display_title = models.BooleanField(default=True)
    sites = models.ManyToManyField(
        'sites.Site',
        blank=True,
        null=True,
        help_text='Sites that this page will appear on.',
    )

    objects = DefaultManager()
    permitted = PermittedManager()
    implements(ITileProvider)

    class Meta:
        ordering = ('title', 'subtitle')

    def __unicode__(self):
        if self.subtitle:
            return '%s (%s)' % (self.title, self.subtitle)
        else:
            return self.title


class Navbar(CachingMixin):
    """A tile navbar contains ordered links"""
    title = models.CharField(max_length=255, help_text='This title is not displayed on the site.')
    subtitle = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text='Some titles may be the same. A subtitle makes a distinction. It is not displayed on the site.',
    )
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
    )

    sites = models.ManyToManyField(
        'sites.Site',
        blank=True,
        null=True,
        help_text='Sites that this page will appear on.',
    )

    objects = DefaultManager()
    permitted = PermittedManager()
    implements(ITileProvider)

    class Meta:
        ordering = ('title', 'subtitle')

    def __unicode__(self):
        if self.subtitle:
            return '%s (%s)' % (self.title, self.subtitle)
        else:
            return self.title


class Listing(models.Model):
    """A themed, ordered collection of items"""
    title = models.CharField(
        max_length=256,
        help_text='A short descriptive title.',
    )
    subtitle = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text='Some titles may be the same. A subtitle makes a distinction. It is not displayed on the site.',
    )
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
    )
    content_type = models.ManyToManyField(
        ContentType,
        help_text="Content types to display, eg. post or gallery.",
        blank=True,
        null=True,
    )
    content = models.ManyToManyField(
        'jmbo.ModelBase',
        help_text="""Individual items to display. Setting this will ignore \
any setting for <i>Content Type</i>, <i>Categories</i> and <i>Tags</i>.""",
        blank=True,
        null=True,
        related_name='listing_content',
        through='ListingContent',
    )
    categories = models.ManyToManyField(
        'category.Category',
        help_text="Categories for which to collect items.",
        blank=True,
        null=True,
        related_name='listing_categories'
    )
    tags = models.ManyToManyField(
        'category.Tag',
        help_text="Tags for which to collect items.",
        blank=True,
        null=True,
        related_name='listing_tags'
    )
    pinned = models.ManyToManyField(
        'jmbo.ModelBase',
        help_text="""Individual items to pin to the top of the listing. These
items are visible across all pages when navigating the listing.""",
        blank=True,
        null=True,
        related_name='listing_pinned',
        through='ListingPinned',
    )
    count = models.IntegerField(
        help_text="""Number of items to display (excludes any pinned items).
Set to zero to display all items.""",
    )
    style = models.CharField(
        choices=[(klass.__name__, klass.__name__) for klass in LISTING_CLASSES],
        max_length=64
    )
    items_per_page = models.PositiveIntegerField(
        default=0,
        help_text="Number of items displayed on a page (excludes any pinned items). Set to zero to disable paging."
    )
    view_modifier = models.CharField(
        'Ordering and filtering',
        max_length=255,
        help_text="""A set of links to order or filter the listing,
eg. 'most liked' or 'most commented'. DefaultViewModifier provided by Jmbo works for
all listings; however, others may be very specific and not work with the listing.""",
        blank=True,
        null=True,
        default=''
    )
    display_title_tiled = models.BooleanField(
        "Display title if in a tile",
        default=True,
        help_text="""Display the title if used as a tile within a more
complex page."""
    )
    enable_syndication = models.BooleanField(default=False)
    sites = models.ManyToManyField(
        'sites.Site',
        blank=True,
        null=True,
        help_text='Sites that this listing will appear on.',
    )

    objects = DefaultManager()
    permitted = PermittedManager()
    implements(ITileProvider)

    class Meta:
        ordering = ('title', 'subtitle')

    def __unicode__(self):
        if self.subtitle:
            return '%s (%s)' % (self.title, self.subtitle)
        else:
            return self.title

    def get_absolute_url(self):
        return reverse('listing-detail', args=[self.slug])

    def queryset(self, request=None):
        q = ModelBase.permitted.filter(id__in=self.content.all())
        if not q.exists():
            q = ModelBase.permitted.all()
            one_match = False
            if self.content_type.exists():
                q = q.filter(content_type__in=self.content_type.all())
                one_match = True
            if self.categories.exists():
                q1 = Q(primary_category__in=self.categories.all())
                q2 = Q(categories__in=self.categories.all())
                q = q.filter(q1|q2)
                one_match = True
            if self.tags.exists():
                q = q.filter(tags__in=self.tags.all())
                one_match = True
            if not one_match:
                q = ModelBase.objects.none()
        q = q.exclude(id__in=self.pinned.all())

        if request and self.view_modifier:
            mod, attr = self.view_modifier.rsplit('.', 1)
            modifier = getattr(import_module(mod), attr)(request)
            # Play along with existing Jmbo view modifier code. We use a shim
            # view for that.
            class ViewShim: params = {}
            view = ViewShim()
            view.params['queryset'] = q
            modifier.modify(view)
            q = view.params['queryset']

        if self.count:
            q = q[:self.count]

        return q

    def set_pinned(self, iterable):
        for n, obj in enumerate(iterable):
            ListingPinned.objects.create(
                modelbase_obj=obj, listing=self, position=n
            )

    def set_content(self, iterable):
        for n, obj in enumerate(iterable):
            ListingContent.objects.create(
                modelbase_obj=obj, listing=self, position=n
            )

    @property
    def pinned_queryset(self):
        # See https://docs.djangoproject.com/en/1.8/topics/db/queries/#using-a-custom-reverse-manager.
        # Django 1.7 will remove the need for this slow workaround.
        li = [o for o in ModelBase.permitted.filter(listing_pinned=self)]
        order = [o.modelbase_obj.id for o in ListingPinned.objects.filter(
            listing=self).order_by('position')]
        li.sort(lambda a, b: cmp(order.index(a.id), order.index(b.id)))
        return AttributeWrapper(li, exists=len(li))

    @property
    def content_queryset(self):
        # See https://docs.djangoproject.com/en/1.8/topics/db/queries/#using-a-custom-reverse-manager.
        # Django 1.7 will remove the need for this slow workaround.
        li = [o for o in ModelBase.permitted.filter(listing_content=self)]
        order = [o.modelbase_obj.id for o in ListingContent.objects.filter(
            listing=self).order_by('position')]
        li.sort(lambda a, b: cmp(order.index(a.id), order.index(b.id)))
        return AttributeWrapper(li, exists=len(li))


class ListingContent(models.Model):
    """Through model to facilitate ordering"""
    modelbase_obj = models.ForeignKey('jmbo.ModelBase')
    listing = models.ForeignKey(Listing, related_name='content_link_to_listing')
    position = models.PositiveIntegerField(default=0)


class ListingPinned(models.Model):
    """Through model to facilitate ordering"""
    modelbase_obj = models.ForeignKey('jmbo.ModelBase')
    listing = models.ForeignKey(Listing, related_name='pinned_link_to_listing')
    position = models.PositiveIntegerField(default=0)


class AbstractLinkPosition(models.Model):
    link = models.ForeignKey(Link)
    position = models.IntegerField()
    name = models.CharField(
        max_length=200, null=True, blank=True,
        help_text="A name that is applied to the link tag.",
    )
    class_name = models.CharField(
        max_length=200, null=True, blank=True,
        help_text="One or more CSS classes that are applied to the link tag.",
    )
    condition_expression = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='A python expression. Variable request is in scope.'
    )

    class Meta:
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

    site_description = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text="A sentence describing the site."
    )
    about_us = RichTextField(null=True, blank=True)
    terms_and_conditions = RichTextField(null=True, blank=True)
    privacy_policy = RichTextField(null=True, blank=True)
    private_site = models.BooleanField(
        default=False,
        help_text=_("A private site requires a visitor to be logged in to view any content."),
    )
    show_age_gateway = models.BooleanField(default=False)
    exempted_urls = models.TextField(
        blank=True,
        default='',
        help_text='''URL patterns that are exempted from the Private Site and \
Age Gateway. Certain URLs like /login are already protected and do not need \
to be listed. One entry per line. Matches are wildcard by default, eg. \
/my-page will match /my-pages/the-red-one.'''
    )
    exempted_ips = models.TextField(
        "Exempted IP addresses",
        blank=True,
        default='',
        help_text='''IP address patterns that are exempted from the Private Site and \
Age Gateway. Matches are wildcard by default, eg. \
192.168.0 will match 192.168.0.5.'''
    )
    analytics_tags = models.TextField(
        null=True,
        blank=True,
        help_text="""May contain tags and javascript. Set this even if the
preference is for a mobile site."""
    )
    exempted_user_agents = models.TextField(
        "Exempted user agents",
        blank=True,
        default='Googlebot\nTwitterbot\nfacebookexternalhit\n',
        help_text='''User agents patterns that are exempted from only the Age Gateway.
This is useful when wanting to share content that is protected by an age
gateway with eg. Facebook. Matches are wildcard by default, eg. \
my-user-agent will match my-user-agent-version-two.'''
    )
    analytics_tags = models.TextField(
        null=True,
        blank=True,
        help_text="""May contain tags and javascript. Set this even if the
preference is for a mobile site."""
    )
    partner_site_configuration = models.TextField(
        null=True,
        blank=True,
        help_text="A list of partner domains and JWT keys, one "
                  "per line. A line has the format &lt;domain&gt; "
                  "&lt;key&gt;, e.g. www.example.com this_is_a_key. "
                  "Partner sites use the JWT key to encode age "
                  "gateway values, etc."
    )

    class Meta:
        verbose_name_plural = 'General Preferences'


class RegistrationPreferences(Preferences):
    __module__ = 'preferences.models'

    raw_display_fields = models.CharField(
        'Display fields',
        max_length=256,
        default='',
        help_text=_('Fields to display on the registration form.')
    )
    raw_required_fields = models.CharField(
        'Required fields',
        max_length=256,
        default='',
        blank=True,
        help_text=_('Set fields which are not required by default as required on the registration form.')
    )
    raw_unique_fields = models.CharField(
        'Unique fields',
        max_length=256,
        default='',
        blank=True,
        help_text=_('Set fields which must be unique on the registration form.')
    )
    raw_field_order = models.CharField(
        'Field order',
        max_length=1024,
        default='{}',
        blank=True,
        help_text=_('Set the ordering of fields on the registration form (opt-in fields are always last).')
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

    @property
    def field_order(self):
        return json.loads(self.raw_field_order)

    def __init__(self, *args, **kwargs):
        super(RegistrationPreferences, self).__init__(*args, **kwargs)
        if not self.field_order:
            index = 0
            field_order_dict = {}
            for f in Member._meta.fields:
                if f.name != 'id':
                    field_order_dict[f.name] = index
                    index += 1
            self.raw_field_order = json.dumps(field_order_dict)

    def save(self, *args, **kwargs):
        # Unique fields must be unique! Check the existing members for possible
        # duplicate values. For example, if mobile number was not a unique
        # field before but it is now, then there may not be two members with
        # the same mobile number.
        for fieldname in self.unique_fields:
            li = Member.objects.exclude(**{fieldname: None}).exclude(
                **{fieldname: ''}).values(fieldname).annotate(
                dcount=Count(fieldname)).order_by('-dcount')
            if li and li[0]['dcount'] > 1:
                raise RuntimeError(
                    "Cannot set %s to be unique since there is more than one \
member with the same %s %s." % (fieldname, fieldname, li[0][fieldname])
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


class NaughtyWordPreferences(Preferences):
    __module__ = 'preferences.models'

    entries = models.TextField(
        default='',
        help_text='''Each line has format "word,weight", eg. "bomb,8". \
Weight must be a value from 1 to 10.'''
    )
    threshold = models.PositiveIntegerField(
        default=5,
        help_text="""An item is deemed suspect if its weighted score exceeds \
this value."""
    )
    email_recipients = models.TextField(
        default='',
        help_text="""Reports are sent to these email addresses. One email \
address per line."""
    )

    class Meta:
        verbose_name_plural = 'Naughty Word Preferences'


class Country(models.Model):
    """Countries used in the age gateway"""
    title = models.CharField(max_length=50)
    slug = models.SlugField(
        editable=True,
        max_length=50,
        unique=True,
    )
    minimum_age = models.PositiveIntegerField(default=18)
    country_code = models.CharField(
        max_length=2,
        null=True,
        blank=False,
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('title',)

    def __unicode__(self):
        return self.title


class Member(User, AbstractAvatarProfile, AbstractSocialProfile, AbstractPersonalProfile, AbstractContactProfile, AbstractSubscriptionProfile, AbstractLocationProfile):
    """Class that models the default user account. Subclassing is superior to profiles since
    a site may conceivably have more than one type of user account, but the profile architecture
    limits the entire site to a single type of profile."""

    country = models.ForeignKey(Country, null=True, blank=True, verbose_name=_('Country'))
    is_profile_complete = models.BooleanField(default=False, editable=False)
    last_seen = models.DateTimeField(null=True, editable=False, db_index=True)
    objects = UserManager()

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.is_profile_complete = True
        required_fields = preferences.RegistrationPreferences.required_fields
        for name in required_fields:
            if not getattr(self, name, None):
                self.is_profile_complete = False
                break

        super(Member, self).save(*args, **kwargs)

        if not self.image:
            # Set a default avatar
            avatars = DefaultAvatar.objects.all().order_by('?')
            if avatars.exists():
                # Note you must use the name attribute else the assignment is
                # by reference. Any event handler that does self.image.save
                # will then change the default avatar.
                self.image.name = avatars[0].image.name
                # Recursion prevented because predicate is changed
                self.save()


    @property
    def last_5_comments(self):
        """Return last 5 comments made by the member"""
        return FoundryComment.objects.filter(user=self).order_by('id')[:5]

    @property
    def number_of_comments(self):
        """Return number of comments made by the member"""
        return FoundryComment.objects.filter(user=self).count()

    @property
    def has_notifications(self):
        """Return true if member has notifications"""
        return self.notification_set.all().exists()


class DefaultAvatar(ImageModel):
    """A set of avatars users can choose from"""
    pass


class Page(models.Model):
    title = models.CharField(
        max_length=200, help_text='A title that may appear in the browser window caption.',
    )
    subtitle = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text='Some titles may be the same. A subtitle makes a distinction. It is not displayed on the site.',
    )
    description = models.TextField(
        help_text=_('A short description. More verbose than the title but \
limited to one or two sentences.'),
        blank=True,
        null=True,
    )
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
    )
    is_homepage = models.BooleanField(default=False, help_text="Tick if you want this page to be the site's homepage.")
    css = models.TextField(
        blank=True,
        null=True,
        help_text="""Additional styling to be applied to the page. This is \
useful when using a page as a campaign."""
    )
    sites = models.ManyToManyField(
        'sites.Site',
        blank=True,
        null=True,
        help_text='Sites that this page will appear on.',
    )

    objects = DefaultManager()
    permitted = PermittedManager()

    def __unicode__(self):
        if self.subtitle:
            return '%s (%s)' % (self.title, self.subtitle)
        else:
            return self.title

    @property
    def rows(self):
        """Fetch rows, columns and tiles in a single query"""

        key = 'foundry-page-rows-%s' % self.id
        cached = cache.get(key, None)
        if cached:
            return cPickle.loads(cached)

        # Organize into a structure
        tiles = Tile.objects.select_related().filter(column__row__page=self).order_by('index')
        struct = {}
        for tile in tiles:
            row = tile.column.row
            if row not in struct:
                struct.setdefault(row, {})
            column = tile.column
            if column not in struct[row]:
                struct[row].setdefault(column, [])
            struct[row][column].append(tile)

        # Sort rows and columns in the structure
        result = []
        keys_row = struct.keys()
        keys_row.sort(lambda a, b: cmp(a.index, b.index))
        for row in keys_row:
            keys_column = struct[row].keys()
            keys_column.sort(lambda a, b: cmp(a.index, b.index))
            column_objs = []
            for column in keys_column:
                column_objs.append(AttributeWrapper(column, tiles=struct[row][column]))
            result.append(AttributeWrapper(row, columns=column_objs))

        cache.set(key, cPickle.dumps(result), settings.FOUNDRY.get('layout_cache_time', 60))

        return result

    @property
    def rows_admin(self):
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
        return sum([o.render_height+20 for o in self.rows_admin])


class PageView(models.Model):
    """We need this bridging class for fast lookups"""
    page = models.ForeignKey(Page)
    view_name = models.CharField(
        max_length=200, help_text='A view that uses the target page to render itself.',
    )

    def __unicode__(self):
        return '%s > %s' % (self.page.title, self.view_name)


class Row(CachingMixin):
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
    has_left_or_right_column = models.BooleanField(default=False, editable=False, db_index=True)
    class_name = models.CharField(
        max_length=200, null=True, blank=True,
        help_text="One or more CSS classes that are applied to the row.",
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.index = self.page.row_set.count()

        if self.id:
            # Aggregate has_left_or_right_column
            self.has_left_or_right_column = False
            for column in self.column_set.all():
                if column.designation in ('left', 'right'):
                    self.has_left_or_right_column = True
                    break

        super(Row, self).save(*args, **kwargs)

    @property
    def columns(self):
        """Fetch columns and tiles in a single query"""
        # Organize into a structure
        struct = {}
        tiles = Tile.objects.select_related().filter(column__row=self).order_by('index')
        for tile in tiles:
            column = tile.column
            if column not in struct:
                struct.setdefault(column, [])
            struct[column].append(tile)

        # Sort columns in the structure
        result = []
        keys_column = struct.keys()
        keys_column.sort(lambda a, b: cmp(a.index, b.index))
        for column in keys_column:
            result.append(AttributeWrapper(column, tiles=struct[column]))

        return result

    @property
    def columns_admin(self):
        return self.column_set.all().order_by('index')

    @property
    def render_height(self):
        return max([o.render_height+8 for o in self.columns_admin] + [0]) + 44


class Column(CachingMixin):
    row = models.ForeignKey(Row)
    index = models.PositiveIntegerField(default=0, editable=False)
    width = models.PositiveIntegerField(default=8)
    title = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text='The title is rendered at the top of a column.',
    )
    designation = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        default='',
        choices=(
            ('left', _('Left')),
            ('right', _('Right')),
        ),
        help_text="Applicable to content (green) rows. Used to display columns \
to the left and right of the content block."
    )
    class_name = models.CharField(
        max_length=200, null=True, blank=True,
        help_text="One or more CSS classes that are applied to the column.",
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.index = self.row.column_set.count()
        super(Column, self).save(*args, **kwargs)

        # Save row so aggregation takes place
        self.row.save()

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


class Tile(CachingMixin):
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
        try:
            return eval(self.condition_expression)
        except:
            return False


class FoundryComment(BaseComment):
    """Custom comment class"""
    in_reply_to = models.ForeignKey('self', null=True, blank=True, db_index=True)
    moderated = models.BooleanField(default=False, db_index=True)

    @property
    def replies(self):
        return FoundryComment.objects.filter(in_reply_to=self).order_by('id')

    @property
    def creator(self):
        """Attempt to return member object"""
        if not self.user:
            return None
        try:
            return Member.objects.get(id=self.user_id)
        except Member.DoesNotExist:
            # Happens when comment is not made by a member
            return None

    def can_report(self, request):
        return not self.commentreport_set.filter(reporter=request.user).exists()


class CommentReport(models.Model):
    comment = models.ForeignKey(FoundryComment)
    reporter = models.ForeignKey(User)

    def __unicode__(self):
        return self.comment.comment


class ChatRoom(ModelBase):
    pass


class BlogPost(ModelBase):
    content = RichTextField(_("Content"))

    def save(self, *args, **kwargs):
        if SCRIPT_REGEX.search(self.content):
            raise RuntimeError("Script in content!")
        super(BlogPost, self).save(*args, **kwargs)


class Notification(models.Model):
    member = models.ForeignKey(Member)
    link = models.ForeignKey(Link)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.id)


class ViewProxy(ModelBase):
    """Content type that allows a view to be used in a listing"""

    view_name = models.CharField(
        max_length=256,
        help_text=_("View name to which this link will redirect."),
    )

    class Meta:
        verbose_name = _("View Proxy")
        verbose_name_plural = _("View Proxies")

    def get_absolute_url(self):
        return None


# todo: move to eventhandlers.py
@receiver(m2m_changed)
def check_slug(sender, **kwargs):
    """Slug must be unique per site"""
    instance = kwargs['instance']
    if (kwargs['action'] == 'post_add') \
        and sender.__name__.endswith('_sites') \
        and isinstance(instance, (Navbar, Menu, Listing, Page)):
        for site in instance.sites.all():
            q = instance.__class__.objects.filter(slug=instance.slug, sites=site).exclude(id=instance.id)
            if q.exists():
                raise RuntimeError("The slug %s is already in use for site %s by %s" % (instance.slug, site.domain, q[0].title))


# Custom fields to be handled by south
add_introspection_rules([], ["^ckeditor\.fields\.RichTextField"])
