from django.conf import settings

def generate():
    objects = [
        {
            "model": "generic.Link",
            "fields": {
                "title": "News",
                "category": {
                    "model": "category.Category",
                    "fields": {
                        "title": "News",
                        "slug": "news",
                    },
                },
            },
        },
        {
            "model": "generic.NavbarLinkPosition",
            "fields": {
                "position": 1,
                "link": {
                    "model": "generic.Link",
                    "fields": {
                        "title": "Home",
                        "view_name": "home",
                    },
                },
                "preferences": {
                    "model": "preferences.NavbarPreferences",
                    "fields": {
                        "sites": settings.SITE_ID,
                    },
                },
            },
        },
        {
            "model": "generic.NavbarLinkPosition",
            "fields": {
                "position": 2,
                "link": {
                    "model": "generic.Link",
                    "fields": {
                        "title": "News"
                    },
                },
                "preferences": {
                    "model": "preferences.NavbarPreferences",
                    "fields": {
                        "sites": settings.SITE_ID,
                    },
                },
            },
        },
        {
            "model": "generic.MenuLinkPosition",
            "fields": {
                "position": 1,
                "link": {
                    "model": "generic.Link",
                    "fields": {
                        "title": "Home",
                        "view_name": "home",
                    },
                },
                "preferences": {
                    "model": "preferences.MenuPreferences",
                    "fields": {
                        "sites": settings.SITE_ID,
                    },
                },
            },
        },
        {
            "model": "generic.MenuLinkPosition",
            "fields": {
                "position": 2,
                "link": {
                    "model": "generic.Link",
                    "fields": {
                        "title": "News"
                    },
                },
                "preferences": {
                    "model": "preferences.MenuPreferences",
                    "fields": {
                        "sites": settings.SITE_ID,
                    },
                },
            },
        },
    ] 

    for i in range(1, 14):
        objects.append({
            "model": "post.Post",
            "fields": {
                "title": "News Post %s" % i,
                "state": "published",
                "sites": settings.SITE_ID,
                "categories": [{
                    "model": "category.Category",
                    "fields": {
                        "title": "News",
                        "slug": "news",
                    },
                },]
            },
        })
    return objects
