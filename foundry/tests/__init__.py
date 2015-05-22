from calendar import timegm
from datetime import datetime, date
from time import sleep
import inspect
import jwt
import os

from django.core import management
from django.core.cache import cache
from django.db import models
from django.test import TestCase as BaseTestCase
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client, RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth.signals import user_logged_in
import django.contrib.sites.models
from django.contrib.sites.models import Site
from django.utils import timezone
from django.db.models.fields import BigIntegerField, BooleanField, CharField, \
    CommaSeparatedIntegerField, DateField, DateTimeField, DecimalField, \
    EmailField, FilePathField, FloatField, IPAddressField, IntegerField, \
    NullBooleanField, PositiveIntegerField, PositiveSmallIntegerField, \
    SlugField, SmallIntegerField, TextField, AutoField
from django.db.models.fields.files import ImageField
from django.db.models.fields.related import OneToOneField
from django.core.files.base import ContentFile
from django.conf import settings

from preferences import preferences
from category.models import Category, Tag
from jmbo.models import ModelBase
from post.models import Post
from zope.interface import implementedBy

from foundry.models import Member, Listing, Page, Row, Column, Tile, \
    Country, Menu, Navbar, ViewProxy
from foundry import views
from foundry.middleware import AG_TOKEN_PARAMETER_NAME, \
    AG_TOKEN_MAX_TIME_TO_EXPIRY
from foundry.utils import get_preference, generate_random_key
from foundry.templatetags.listing_styles import LISTING_CLASSES


RES_DIR = os.path.join(os.path.dirname(__file__), "res")
IMAGE_PATH = os.path.join(RES_DIR, "image.jpg")


def set_image(obj):
    obj.image.save(
        os.path.basename(IMAGE_PATH),
        ContentFile(open(IMAGE_PATH, "rb").read())
    )


class TestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        cls.request = RequestFactory()
        cls.client = Client()

        # Post-syncdb steps
        management.call_command('load_photosizes', interactive=False)

        # Editor
        cls.editor, dc = Member.objects.get_or_create(
            username='editor',
            email='editor@test.com'
        )
        cls.editor.set_password("password")
        cls.editor.save()

        # Add an extra site
        site, dc = Site.objects.get_or_create(name='mobi', domain='mobi.com')

        # Categories
        for i in range(1, 5):
            cat, dc = Category.objects.get_or_create(
                title='Category %s' % i, slug='cat%s' % i
            )
            cat.sites = [1]
            cat.save()
            setattr(cls, 'cat%s' % i, cat)

        # Tags
        for i in range(1, 5):
            tag, dc = Tag.objects.get_or_create(
                title='Tag %s' % i, slug='tag%s' % i
            )
            tag.sites = [1]
            tag.save()
            setattr(cls, 'tag%s' % i, tag)

        # Published posts
        for i in range(1, 5):
            post, dc = Post.objects.get_or_create(
                title='Post %s' % i, content='<b>aaa</b>',
                owner=cls.editor, state='published',
            )
            # Toggle between categories and primary category
            if i % 2 == 1:
                post.categories = [getattr(cls, 'cat%s' % i)]
                post.tags = [getattr(cls, 'tag%s' % i)]
            else:
                post.primary_category = getattr(cls, 'cat%s' % i)
            post.sites = [1]
            set_image(post)
            post.save()
            setattr(cls, 'post%s' % i, post)

        # Unpublished posts
        for i in range(5,7):
            post, dc = Post.objects.get_or_create(
                title='Post %s' % i, content='<b>aaa</b>',
                owner=cls.editor, state='unpublished',
            )
            post.sites = [1]
            set_image(post)
            post.save()
            setattr(cls, 'post%s' % i, post)

        # Published galleries
        if "gallery" in settings.INSTALLED_APPS:
            from gallery.models import Gallery
            for i in range(1, 5):
                gallery, dc = Gallery.objects.get_or_create(
                    title='Gallery %s' % i, owner=cls.editor, state='published',
                )
                # Toggle between categories and primary category
                if i % 2 == 1:
                    gallery.categories = [getattr(cls, 'cat%s' % i)]
                    gallery.tags = [getattr(cls, 'tag%s' % i)]
                else:
                    gallery.primary_category = getattr(cls, 'cat%s' % i)
                gallery.sites = [1]
                set_image(gallery)
                gallery.save()
                setattr(cls, 'gallery%s' % i, Gallery)

        # Listings

        # Content-type
        content_type = ContentType.objects.get(app_label='post', model='post')
        listing_pvt, dc = Listing.objects.get_or_create(
            title='Posts vertical thumbnail',
            slug='posts-vertical-thumbnail',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_pvt.content_type = [content_type]
        listing_pvt.sites = [1]
        listing_pvt.save()
        setattr(cls, listing_pvt.slug, listing_pvt)

        # Content points to only published content
        listing_pc, dc = Listing.objects.get_or_create(
            title='Published content',
            slug='published-content',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_pc.sites = [1]
        listing_pc.save()
        listing_pc.set_content([cls.post1])
        setattr(cls, listing_pc.slug, listing_pc)

        # Content points to unpublished content
        listing_upc, dc = Listing.objects.get_or_create(
            title='Unpublished content',
            slug='unpublished-content',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_upc.sites = [1]
        listing_upc.save()
        listing_upc.set_content([cls.post1, cls.post5])
        setattr(cls, listing_upc.slug, listing_upc)

        # Pinned items
        listing_pinned, dc = Listing.objects.get_or_create(
            title='Listing pinned',
            slug='listing-pinned',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_pinned.sites = [1]
        listing_pinned.save()
        listing_pinned.set_pinned([cls.post1])
        setattr(cls, listing_pinned.slug, listing_pinned)

        # Listing with categories
        listing_categories, dc = Listing.objects.get_or_create(
            title='Listing categories',
            slug='listing-categories',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_categories.categories = [cls.cat1, cls.cat2]
        listing_categories.sites = [1]
        listing_categories.save()
        setattr(cls, listing_categories.slug, listing_categories)\

        # Listing with tags
        listing_tags, dc = Listing.objects.get_or_create(
            title='Listing tags',
            slug='listing-tags',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_tags.tags = [cls.tag1, cls.tag2]
        listing_tags.sites = [1]
        listing_tags.save()
        setattr(cls, listing_tags.slug, listing_tags)

        # Listing with content_type, categories and tags
        content_type = ContentType.objects.get(app_label='post', model='post')
        listing_all, dc = Listing.objects.get_or_create(
            title='Listing all filters',
            slug='listing-all-filters',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_all.content_type = [content_type]
        listing_all.categories = [cls.cat1, cls.cat2]
        listing_all.tags = [cls.tag1, cls.tag2]
        listing_all.sites = [1]
        listing_all.save()
        setattr(cls, listing_all.slug, listing_all)

        # Listings for each style
        content_type = ContentType.objects.get(app_label='post', model='post')
        for klass in LISTING_CLASSES:
                style = klass.__name__
                listing, dc = Listing.objects.get_or_create(
                    title='Listing %s' % style,
                    slug='listing-%s' % style.lower(),
                    count=0, items_per_page=0, style=style,
                )
                listing.sites = [1]
                listing.save()
                listing.set_pinned([cls.post1])
                setattr(cls, listing.slug, listing)

        # Page with row, column and tile
        page, dc = Page.objects.get_or_create(title='A page', slug='a-page')
        page.sites = [1]
        page.save()
        setattr(cls, page.slug, page)
        row, dc = Row.objects.get_or_create(id=1, page=page)
        column, dc = Column.objects.get_or_create(id=1, row=row)
        tile, dc = Tile.objects.get_or_create(id=1, column=column)
        tile.view_name = 'test-plain-response'
        tile.enable_caching = True
        tile.cache_timeout = 5
        tile.save()

        # A few members
        member, dc = Member.objects.get_or_create(username='jannie')
        member.email = 'jannie@aaa.com'
        member.save()
        setattr(cls, 'jannie', member)
        member, dc = Member.objects.get_or_create(username='pietie')
        member.email = 'pietie@aaa.com'
        member.save()
        setattr(cls, 'pietie', member)
        member, dc = Member.objects.get_or_create(username='klaas')
        member.email = ''
        member.save()
        setattr(cls, 'klaas', member)

    def test_tileproviders(self):
        tileproviders = [
            m for m in models.get_models()
            if "ITileProvider" in [
                interface.getName() for interface in implementedBy(m)
            ]
        ]
        for tileprovider in [Menu, Listing, Navbar]:
            self.assertIn(tileprovider, tileproviders)

    def test_listing_pvt(self):
        listing = getattr(self, 'posts-vertical-thumbnail')
        self.failUnless(self.post1.modelbase_obj in listing.queryset().all())

    def test_listing_pc(self):
        # Published content must be present in listing queryset
        listing = getattr(self, 'published-content')
        self.failUnless(self.post1.modelbase_obj in listing.queryset().all())

    def test_listing_upc(self):
        # Unpublished content must not be present in listing queryset
        listing = getattr(self, 'unpublished-content')
        self.failIf(self.post5.modelbase_obj in listing.queryset().all())

    def test_listing_pinned(self):
        listing = getattr(self, 'listing-pinned')
        self.failIf(self.post1.modelbase_obj in listing.queryset().all())

    def test_listing_categories(self):
        listing = getattr(self, 'listing-categories')
        self.failUnless(self.post1.modelbase_obj in listing.queryset().all())
        self.failUnless(self.post2.modelbase_obj in listing.queryset().all())
        self.failIf(self.post3.modelbase_obj in listing.queryset().all())

    def test_listing_tags(self):
        listing = getattr(self, 'listing-tags')
        self.failUnless(self.post1.modelbase_obj in listing.queryset().all())
        self.failIf(self.post2.modelbase_obj in listing.queryset().all())

    def test_listing_all_filters(self):
        listing = getattr(self, 'listing-all-filters')
        self.failUnless(self.post1.modelbase_obj in listing.queryset().all())
        self.failIf(self.post2.modelbase_obj in listing.queryset().all())
        self.failIf(self.post3.modelbase_obj in listing.queryset().all())
        if "gallery" in settings.INSTALLED_APPS:
            self.failIf(self.gallery1.modelbase_obj in listing.queryset().all())

    def test_listing_styles(self):
        """Confirm the listings of each style render"""
        for klass in LISTING_CLASSES:
                response = self.client.get('/listing/listing-%s/' % klass.__name__.lower())
                self.assertEqual(response.status_code, 200)

    def test_pages(self):
        # Login, password reset
        for name in ('login', 'password_reset'):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.failIf(response.content.find('foundry-form') == -1)

        # Posts vertical thumbnail listing
        response = self.client.get('/listing/posts-vertical-thumbnail/')
        self.assertEqual(response.status_code, 200)
        self.failIf(response.content.find('foundry-listing-vertical-thumbnail') == -1)
        self.failIf(response.content.find('/post/cat1/post-1') == -1)

    def test_last_seen(self):
        self.editor.last_seen = None
        self.editor.save()
        self.client.cookies.clear()
        # login sends dud request without REQUEST dict
        user_logged_in.disconnect(views.set_session_expiry)
        self.client.login(username="editor", password="password")
        user_logged_in.connect(views.set_session_expiry)
        self.client.get("/")
        last_seen = Member.objects.get(pk=self.editor.pk).last_seen
        self.assertTrue(last_seen)
        self.client.get("/")
        self.assertEqual(Member.objects.get(pk=self.editor.pk).last_seen, last_seen)

    def test_caching(self):
        # Render page and grab timestamp in template
        response = self.client.get('/page/a-page/')
        control_now_string = response.content.split('NOW_MARKER')[1]

        # Next call must still be cached
        sleep(2)
        response = self.client.get('/page/a-page/')
        now_string = response.content.split('NOW_MARKER')[1]
        self.assertEqual(now_string, control_now_string)

        # Next call the cache must be expired
        sleep(4)
        response = self.client.get('/page/a-page/')
        now_string = response.content.split('NOW_MARKER')[1]
        self.assertNotEqual(now_string, control_now_string)

    def test_registration_preferences(self):
        rp = preferences.RegistrationPreferences

        # Initialize
        rp.raw_unique_fields = 'email'
        rp.save()

        # Cause a collision
        self.klaas.email = 'jannie@aaa.com'
        self.klaas.save()
        rp.raw_unique_fields = 'email'
        self.assertRaises(RuntimeError, rp.save)

        # Empty emails do not cause collisions
        self.jannie.email = ''
        self.jannie.save()
        self.klaas.email = ''
        self.klaas.save()
        rp.raw_unique_fields = 'email'
        rp.save()

    def test_get_preference(self):
        # Set about us for each site
        gp1 = preferences.GeneralPreferences
        gp1.about_us = 'gp1'
        gp1.save()
        settings.SITE_ID = 2
        django.contrib.sites.models.SITE_CACHE = {}
        gp2 = preferences.GeneralPreferences
        gp2.about_us = 'gp2'
        gp2.save()
        settings.SITE_ID = 1
        django.contrib.sites.models.SITE_CACHE = {}

        # Test that there is no cache key collision
        about1 = get_preference('GeneralPreferences', 'about_us')
        settings.SITE_ID = 2
        django.contrib.sites.models.SITE_CACHE = {}
        about2 = get_preference('GeneralPreferences', 'about_us')
        settings.SITE_ID = 1
        django.contrib.sites.models.SITE_CACHE = {}
        self.assertNotEqual(about1, about2)

    def test_common_urls(self):
        """High-level test to confirm common set of URLs render"""
        urls = (
            (reverse('join'), 200),
            (reverse('login'), 200),
            (reverse('logout'), 302),
            (reverse('password_reset'), 200),
            (reverse('terms-and-conditions'), 200),
            #('/sitemap.xml', 200), # restore once sitemap is back in tests_require
        )
        for url, code in urls:
            print "Checking path %s" % url
            response = self.client.get(url)
            self.assertEqual(response.status_code, code)

    def test_detail_pages(self):
        """Create an instance of each Jmbo content type and render detail
        page"""

        modelbase_fieldnames = [f.name for f in ModelBase._meta.fields]

        for ct in ContentType.objects.all():
            model_class = ct.model_class()

            # Skip over BaseImageBanner because it mangles get_absolute_url
            try:
                from banner.models import BaseImageBanner
            except ImportError:
                pass
            else:
                if issubclass(model_class, BaseImageBanner):
                    continue

            # Skip over Download until we upload a file for it in the test
            try:
                from downloads.models import Download
            except ImportError:
                pass
            else:
                if issubclass(model_class, Download):
                    continue

            # Skip over ViewProxy since it has no detail view
            if issubclass(model_class, ViewProxy):
                continue

            if (model_class is not None) \
                and issubclass(model_class, ModelBase):

                di = dict(
                    title=model_class.__name__,
                    description='Description',
                    state='published',
                    owner=self.editor,
                )

                # Set not null fields if possible
                skip = False
                for field in model_class._meta.fields:
                    if field.name in modelbase_fieldnames:
                        continue
                    if field.name in di:
                        continue
                    if not field.null:
                        if isinstance(field, (IntegerField, SmallIntegerField,
                            BigIntegerField, PositiveIntegerField,
                            PositiveSmallIntegerField)):
                            di[field.name] = 1
                        elif isinstance(field, (CharField, TextField)):
                            di[field.name] = 'a'
                        elif isinstance(field, FloatField):
                            di[field.name] = 1.0
                        elif isinstance(field, DateField):
                            di[field.name] = timezone.now().date()
                        elif isinstance(field, DateTimeField):
                            di[field.name] = timezone.now()
                        elif isinstance(field, (BooleanField, NullBooleanField)):
                            di[field.name] = True
                        elif isinstance(field, (AutoField, ImageField,
                            OneToOneField)):
                            pass
                        else:
                            skip = True
                            break

                # Skip if issues expected
                if skip:
                    continue

                # Save. Continue on error. We did our best.
                try:
                    obj = model_class.objects.create(**di)
                except TypeError:
                    continue
                obj.sites = [1]
                set_image(obj)
                obj.save()

                # Test
                print "Checking %s detail page %s" \
                    % (model_class.__name__, obj.get_absolute_url())
                response = self.client.get(obj.get_absolute_url())
                self.assertEqual(response.status_code, 200)

    def test_static_view(self):
        """High-level test to confirm static views render"""
        urls = (
            (reverse("about-us"), "About us"),
            (reverse("terms-and-conditions"), "Terms and conditions"),
            (reverse("privacy-policy"), "Privacy policy"),
        )
        for url, title in urls:
            response = self.client.get(url)
            self.failUnless(title in response.content)


class AgeGatewayTestCase(BaseTestCase):

    def setUp(self):
        super(AgeGatewayTestCase, self).setUp()
        cache.clear()

    @classmethod
    def setUpClass(cls):
        super(AgeGatewayTestCase, cls).setUpClass()
        Country.objects.create(title='South Africa',
                               country_code='ZA',
                               minimum_age=18)
        gp = preferences.GeneralPreferences
        gp.show_age_gateway = True
        gp.save()

    @classmethod
    def tearDownClass(cls):
        super(AgeGatewayTestCase, cls).tearDownClass()
        gp = preferences.GeneralPreferences
        gp.show_age_gateway = False
        gp.save()
        cache.clear()

    def pass_age_gateway(self, dob=None, country_code='ZA', extra={}):
        if dob is None:
            dob = date(day=1, month=7, year=1985)
        data = {
            'country': Country.objects.get(country_code=country_code).pk,
            'remember_me': True,
            'date_of_birth_0': dob.day,
            'date_of_birth_1': dob.month,
            'date_of_birth_2': dob.year
        }
        data.update(extra)
        response = self.client.post(reverse('age-gateway'), data)
        return response

    def test_age_gateway(self):
        self.assertRedirects(self.client.get(reverse('home')),
                             '%s?next=/' % reverse('age-gateway'))
        self.pass_age_gateway()
        self.assertEqual(self.client.get(reverse('home')).status_code,
                         200)

    def test_auto_pass_age_gateway(self):
        partner_domain = 'www.test.com'
        partner_key = generate_random_key(50)
        gp = preferences.GeneralPreferences
        gp.partner_site_configuration = '%s %s' % (partner_domain, partner_key)
        gp.save()

        # create token with over-18 value
        now = timezone.now()
        expiry = now.replace(year=now.year + 10)
        payload = {
            # value of age_gateway_values cookie
            'v': 'ZA-01-07-1985',
            # expiry for age gateway cookies
            'e': expiry.strftime('%Y-%m-%dT%H:%M:%S'),
            # expiry for this payload
            'exp': (timegm(datetime.utcnow().utctimetuple())
                    + int(AG_TOKEN_MAX_TIME_TO_EXPIRY * 0.5))
        }
        token = jwt.encode(payload, partner_key)
        response = self.client.get('%s?%s=%s' % (reverse('home'),
                                                 AG_TOKEN_PARAMETER_NAME,
                                                 token),
                                   HTTP_REFERER='http://%s' % partner_domain)
        self.assertIn('age_gateway_passed', self.client.cookies)
        self.assertEqual(self.client.cookies['age_gateway_passed'].value, '1')
        self.assertEqual(self.client.cookies['age_gateway_passed']['expires'],
                         expiry.strftime('%a, %d-%b-%Y %H:%M:%S GMT'))
        self.assertIn('age_gateway_values', self.client.cookies)
        self.assertEqual(self.client.cookies['age_gateway_values'].value,
                         'ZA-01-07-1985')
        self.assertEqual(response.status_code, 200)

    def test_next_redirect(self):
        redirect_to = reverse('about-us')
        response = self.client.get(redirect_to)
        self.assertRedirects(response,
                             '%s?next=%s' % (reverse('age-gateway'),
                                             redirect_to))
        self.assertContains(self.client.get(response['Location']),
                            'name="next" value="%s"' % redirect_to)
        response = self.pass_age_gateway(extra={'next': redirect_to})
        self.assertRedirects(response,
                             reverse('about-us'))
