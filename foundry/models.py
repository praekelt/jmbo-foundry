import inspect

from django.core.urlresolvers import reverse, Resolver404
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.comments.models import Comment as BaseComment
from django.contrib.sites.models import Site
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils.importlib import import_module
from django.utils import simplejson as json

from ckeditor.fields import RichTextField
from preferences.models import Preferences
from snippetscream import resolve_to_name
from photologue.models import ImageModel
from south.modelsinspector import add_introspection_rules

from jmbo.utils import generate_slug
from jmbo.models import ModelBase
from jmbo.managers import DefaultManager

from foundry.profile_models import AbstractAvatarProfile, \
    AbstractSocialProfile, AbstractPersonalProfile, \
    AbstractContactProfile, AbstractSubscriptionProfile, \
    AbstractLocationProfile
from foundry.templatetags import listing_styles
from foundry.managers import PermittedManager
import foundry.monkey


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


class Menu(models.Model):
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

    class Meta:
        ordering = ('title', 'subtitle')

    def __unicode__(self):
        if self.subtitle:
            return '%s (%s)' % (self.title, self.subtitle)
        else:
            return self.title


class Navbar(models.Model):
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
        help_text="Individual items to display.",
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        'category.Category',
        help_text="Category for which to collect items.",
        blank=True,
        null=True,
    )
    pinned = models.ManyToManyField(
        'jmbo.ModelBase',
        help_text="""Individual items to pin to the top of the listing. These 
items are visible across all pages when navigating the listing.""",
        blank=True,
        null=True,
        related_name='listing_pinned',
    )
    count = models.IntegerField(
        help_text="""Number of items to display (excludes any pinned items). 
Set to zero to display all items.""",
    )
    style = models.CharField(
        choices=((style[0], style[0]) for style in inspect.getmembers(listing_styles, inspect.isclass) if style[0] != 'AbstractBaseStyle'),
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
        q = self.content.all()
        if not q.exists():
            q = ModelBase.permitted.all()
            if self.content_type.exists():
                q = q.filter(content_type__in=self.content_type.all())
            elif self.category:
                q = q.filter(Q(primary_category=self.category)|Q(categories=self.category))
        q = q.exclude(id__in=self.pinned.all().values_list('id', flat=True))

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

    @property
    def pinned_queryset(self):
        return self.pinned.all()
        

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
            values = Member.objects.exclude(**{fieldname: None}).values_list(fieldname, flat=True)
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

    country = models.ForeignKey(Country, null=True, blank=True)
    
    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):        
        super(Member, self).save(*args, **kwargs)

        # Create / clear notifications on imcomplete / complete fields
        link, dc = Link.objects.get_or_create(
            title=ugettext("Set your profile picture"), view_name='join-finish'
        )
        if not self.image:
            # Set a default avatar
            avatars = DefaultAvatar.objects.all().order_by('?')
            if avatars.exists():
                self.image = avatars[0].image
            Notification.objects.get_or_create(member=self, link=link)
        else:
            try:
                notification = Notification.objects.get(member=self, link=link)
                notification.delete()
            except Notification.DoesNotExist:
                pass

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
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
    )
    is_homepage = models.BooleanField(default=False, help_text="Tick if you want this page to be the site's homepage.")
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


class PageView(models.Model):
    """We need this bridging class for fast lookups"""
    page = models.ForeignKey(Page)
    view_name = models.CharField(
        max_length=200, help_text='A view that uses the target page to render itself.',
    )

    def __unicode__(self):
        return '%s > %s' % (self.page.title, self.view_name)


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
    has_left_or_right_column = models.BooleanField(default=False, editable=False, db_index=True)

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
        return self.column_set.all().order_by('index')

    @property
    def render_height(self):
        return max([o.render_height+8 for o in self.columns] + [0]) + 44

    
class Column(models.Model):
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
    

class Notification(models.Model):
    member = models.ForeignKey(Member)
    link = models.ForeignKey(Link)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.id)


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
