import random

from django.db.models import Max
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from generate import IMAGES
from post.models import Post

from foundry.models import BlogPost

NUMBER_OF_POSTS = 5000
NUMBER_OF_BLOGPOSTS = 5000
NUMBER_OF_COMMENTS = 10000

POST_ID_START = (Post.objects.aggregate(Max('id'))['id__max'] or 0) + 1
BLOGPOST_ID_START = (BlogPost.objects.aggregate(Max('id'))['id__max'] or 0) + 1

CATEGORIES = (
    {
        "model": "category.Category",
        "fields": {
            "title": "News",
            "slug": "news",
          }               
    },
    {
        "model": "category.Category",
        "fields": {
            "title": "Gossip",
            "slug": "gossip",
          }               
    },
    {
        "model": "category.Category",
        "fields": {
            "title": "Trending",
            "slug": "trending",
          }               
    },
    {
        "model": "category.Category",
        "fields": {
            "title": "Celebs",
            "slug": "celebs",
          }               
    },
    {
        "model": "category.Category",
        "fields": {
            "title": "Technical",
            "slug": "technical",
          }               
    },
)

STRINGS = (
    'All the world is a stage',
)

def generate():
    objects = []

    for i in range(POST_ID_START, POST_ID_START+NUMBER_OF_POSTS+1):
        di = {
            "model": "post.Post",
            "fields": {
                "id": i,
                "title": "News Post %s" % i,
                "description": "News Post %s %s long description." % (i, 'very ' * 50),
                "content": "News Post %s <b>%s</b> long safe content." % (i, 'very ' * 100),
                "state": "published",
                "sites": settings.SITE_ID,
                "image": random.sample(IMAGES, 1)[0],
            }
        }
        di['fields']['categories'] = random.sample(CATEGORIES, random.randint(1, len(CATEGORIES)))
        di['fields']['primary_category'] = random.choice(CATEGORIES)
        objects.append(di)

    for i in range(BLOGPOST_ID_START, BLOGPOST_ID_START+NUMBER_OF_BLOGPOSTS+1):
        di = {
            "model": "foundry.BlogPost",
            "fields": {
                "id": i,
                "title": "Blog Post %s" % i,
                "description": "Blog Post %s %s long description." % (i, 'very ' * 50),
                "content": "Blog Post %s <b>%s</b> long safe content." % (i, 'very ' * 100),
                "state": "published",
                "sites": settings.SITE_ID,
                "image": random.sample(IMAGES, 1)[0],
            }
        }
        objects.append(di)

    objects.append({
        "model": "jmbo.Pin",
        "fields": {
            "category": {
                "model": "category.Category",
                "fields": {
                    "slug": "news",
                },
            },
            "content": {
                "model": "post.Post",
                "fields": {
                    "title": "News Post 7",
                },
            },
        },
    })

    # Comments
    ctids = [ContentType.objects.get_for_model(Post).id, ContentType.objects.get_for_model(BlogPost).id]
    for i in range(0, NUMBER_OF_COMMENTS):
        if random.randint(0, 1) == 0:
            ctid = ctids[0]
            pk = random.randint(POST_ID_START, POST_ID_START+NUMBER_OF_POSTS+1)
        else:
            ctid = ctids[1]
            pk = random.randint(BLOGPOST_ID_START, BLOGPOST_ID_START+NUMBER_OF_BLOGPOSTS+1)

        objects.append({
            'model': 'foundry.FoundryComment',
            'fields': {
                'content_type': {
                    'model': 'contenttypes.ContentType',
                    'fields': {
                        'id': int(ctid),
                    }
                },
                'object_pk': pk,
                'site': {
                    'model': 'sites.Site',
                    'fields': {
                        'id': settings.SITE_ID,
                    }
                },
                'user': {
                    'model': 'auth.User',
                    'fields': {
                        'id': 1,
                    }
                },
                'user_name': 'Anonymous%s' % random.randint(0, 10000),
                'user_email': 'anonymous@jmbo.org',
                'user_url': '',
                'comment': random.choice(STRINGS)
            }
        })

    return objects
