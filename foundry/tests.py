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

        # Posts
        for i in range(1, 5):
            post, dc = Post.objects.get_or_create(
                title='Post %s' % i, content='<b>aaa</b>',
                owner=self.editor, state='published',
            )
            post.sites = [1]
            post.save()
            setattr(self, 'post%s' % i, post)

        # Listings
        content_type = ContentType.objects.get(app_label='post', model='post')
        listing, dc = Listing.objects.get_or_create(
            title='Posts vertical thumbnail', 
            slug='posts-vertical-thumbnail',
            count=0, items_per_page=0, style='VerticalThumbnail',
        )
        listing.content_type = [content_type]
        listing.sites = [1]
        listing.save()
        setattr(self, listing.slug, listing)

        setattr(self, '_initialized', 1)

    def test_listing(self):
        listing = getattr(self, 'posts-vertical-thumbnail')
        self.failUnless(self.post1.modelbase_obj in listing.queryset().all())

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

