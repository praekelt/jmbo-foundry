from datetime import datetime
from time import sleep
import inspect

from django.core import management
from django.test import TestCase as BaseTestCase
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client as BaseClient, FakePayload, \
    RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth.signals import user_logged_in
import django.contrib.sites.models
from django.contrib.sites.models import Site
from django.conf import settings

from preferences import preferences
from preferences.models import Preferences
from category.models import Category, Tag
from post.models import Post
from gallery.models import Gallery

from foundry.models import Member, Listing, Page, Row, Column, Tile
from foundry import views
from foundry.utils import get_preference
from foundry.templatetags import listing_styles


class Client(BaseClient):
    """Bug in django/test/client.py omits wsgi.input"""

    def _base_environ(self, **request):
        result = super(Client, self)._base_environ(**request)
        result['HTTP_USER_AGENT'] = 'Django Unittest'
        result['HTTP_REFERER'] = 'dummy'
        result['wsgi.input'] = FakePayload('')
        return result


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
            post.save()
            setattr(cls, 'post%s' % i, post)

        # Unpublished posts
        for i in range(5,7):
            post, dc = Post.objects.get_or_create(
                title='Post %s' % i, content='<b>aaa</b>',
                owner=cls.editor, state='unpublished',
            )
            post.sites = [1]
            post.save()
            setattr(cls, 'post%s' % i, post)

        # Published galleries
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
        listing_pc.content = [cls.post1]
        listing_pc.sites = [1]
        listing_pc.save()
        setattr(cls, listing_pc.slug, listing_pc)

        # Content points to unpublished content
        listing_upc, dc = Listing.objects.get_or_create(
            title='Unpublished content',
            slug='unpublished-content',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_upc.content = [cls.post1, cls.post5]
        listing_upc.sites = [1]
        listing_upc.save()
        setattr(cls, listing_upc.slug, listing_upc)

        # Pinned items
        listing_pinned, dc = Listing.objects.get_or_create(
            title='Listing pinned',
            slug='listing-pinned',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_pinned.pinned = [cls.post1]
        listing_pinned.sites = [1]
        listing_pinned.save()
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
        for style, dc in inspect.getmembers(listing_styles, inspect.isclass):
            if style != 'AbstractBaseStyle':
                listing, dc = Listing.objects.get_or_create(
                    title='Listing %s' % style,
                    slug='listing-%s' % style.lower(),
                    count=0, items_per_page=0, style=style,
                )
                listing.pinned = [cls.post1]
                listing.sites = [1]
                listing.save()
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
        self.failIf(self.gallery1.modelbase_obj in listing.queryset().all())

    def test_listing_styles(self):
        """Confirm the listings of each style render"""
        for style, dc in inspect.getmembers(listing_styles, inspect.isclass):
            if style != 'AbstractBaseStyle':
                response = self.client.get('/listing/listing-%s/' % style.lower())
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
        self.failIf(response.content.find('/post/post-1') == -1)

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
