from django.core import management
from django.utils import unittest
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client as BaseClient, FakePayload, \
    RequestFactory
from django.core.urlresolvers import reverse

from post.models import Post

from foundry.models import Member, Listing


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

