from datetime import datetime
from time import sleep

from django.core import management
from django.utils import unittest
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client as BaseClient, FakePayload, \
    RequestFactory
from django.core.urlresolvers import reverse

from preferences import preferences
from post.models import Post

from foundry.models import Member, Listing, Page, Row, Column, Tile


class Client(BaseClient):
    """Bug in django/test/client.py omits wsgi.input"""

    def _base_environ(self, **request):
        result = super(Client, self)._base_environ(**request)
        result['HTTP_USER_AGENT'] = 'Django Unittest'
        result['HTTP_REFERER'] = 'dummy'
        result['wsgi.input'] = FakePayload('')
        return result


class TestCase(unittest.TestCase):

    def setUp(self):
        self.request = RequestFactory()
        self.client = Client()

        # Post-syncdb steps
        management.call_command('migrate', interactive=False)
        management.call_command('load_photosizes', interactive=False)

        # Editor
        self.editor, dc = Member.objects.get_or_create(
            username='editor',
            email='editor@test.com'
        )
        self.editor.set_password("password")
        self.editor.save()

        # Published posts
        for i in range(1, 5):
            post, dc = Post.objects.get_or_create(
                title='Post %s' % i, content='<b>aaa</b>',
                owner=self.editor, state='published',
            )
            post.sites = [1]
            post.save()
            setattr(self, 'post%s' % i, post)

        # Unpublished posts
        for i in range(5,7):
            post, dc = Post.objects.get_or_create(
                title='Post %s' % i, content='<b>aaa</b>',
                owner=self.editor, state='unpublished',
            )
            post.sites = [1]
            post.save()
            setattr(self, 'post%s' % i, post)

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
        setattr(self, listing_pvt.slug, listing_pvt)

        # Content points to only published content
        listing_pc, dc = Listing.objects.get_or_create(
            title='Published content', 
            slug='published-content',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_pc.content = [self.post1]
        listing_pc.sites = [1]
        listing_pc.save()
        setattr(self, listing_pc.slug, listing_pc)

        # Content points to unpublished content
        listing_upc, dc = Listing.objects.get_or_create(
            title='Unpublished content', 
            slug='unpublished-content',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_upc.content = [self.post1, self.post5]
        listing_upc.sites = [1]
        listing_upc.save()
        setattr(self, listing_upc.slug, listing_upc)

        # Pinned items
        listing_pinned, dc = Listing.objects.get_or_create(
            title='Listing pinned', 
            slug='listing-pinned',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing_pinned.pinned = [self.post1]
        listing_pinned.sites = [1]
        listing_pinned.save()
        setattr(self, listing_pinned.slug, listing_pinned)

        # Page with row, column and tile
        page, dc = Page.objects.get_or_create(title='A page', slug='a-page')
        page.sites = [1]
        page.save()
        setattr(self, page.slug, page)
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
        setattr(self, 'jannie', member)
        member, dc = Member.objects.get_or_create(username='pietie')
        member.email = 'pietie@aaa.com'
        member.save()
        setattr(self, 'pietie', member)
        member, dc = Member.objects.get_or_create(username='klaas')
        member.email = ''
        member.save()
        setattr(self, 'klaas', member)

        setattr(self, '_initialized', 1)


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
        self.client.login(username="editor", password="password")
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
