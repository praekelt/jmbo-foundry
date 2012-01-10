import random

from django.db.models import Max
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from generate import IMAGES

from post.models import Post

NUMBER_OF_POSTS = 5000

POST_ID_START = (Post.objects.aggregate(Max('id'))['id__max'] or 0) + 1

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
    for i in range(1, 10000):
        objects.append({
            'model': 'foundry.FoundryComment',
            'fields': {
                'content_type': {
                    'model': 'contenttypes.ContentType',
                    'fields': {
                        'id': int(ContentType.objects.get_for_model(Post).id),
                    }
                },
                'object_pk': random.randint(POST_ID_START, POST_ID_START+NUMBER_OF_POSTS+1),
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
                'user_name': 'Anonymous',
                'user_email': 'anonymous@jmbo.org',
                'user_url': '',
                'comment': random.choice(STRINGS)
            }
        })

    return objects
