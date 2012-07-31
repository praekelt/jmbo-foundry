from django.core import management
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from post.models import Post

from foundry.models import Member, Listing


class TestCase(TestCase):

    def setUp(self):
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
            post = Post.objects.create(
                title='Post %s' % i, content='<b>aaa</b>',
                owner=self.editor, state='published',
            )
            post.sites = [1]
            post.save()
            setattr(self, 'post%s' % i, post)

    def test_listing(self):
        content_type = ContentType.objects.get(app_label='post', model='post')
        posts = Listing.objects.create(
            title='Posts', count=0, style='VerticalThumbnail',
        )
        posts.content_type = [content_type]
        posts.sites = [1]
        posts.save()
        self.failUnless(self.post1.modelbase_obj in posts.queryset.all())
