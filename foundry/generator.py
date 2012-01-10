import random

from django.conf import settings

from generate import IMAGES

def generate():
    objects = []
     
    for i in range(1, 14):
        objects.append({
            "model": "post.Post",
            "fields": {
                "title": "News Post %s" % i,
                "description": "News Post %s %s long description." % (i, 'very ' * 50),
                "content": "News Post %s <b>%s</b> long safe content." % (i, 'very ' * 100),
                "state": "published",
                "sites": settings.SITE_ID,
                "image": random.sample(IMAGES, 1)[0],
                "categories": [
                    {
                        "model": "category.Category",
                        "fields": {
                            "title": "News",
                            "slug": "news",
                        }
                    },
                ],
                "primary_category": {
                    "model": "category.Category",
                    "fields": {
                        "title": "News",
                        "slug": "news",
                    },
                },
            },
        })
    
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

    return objects
