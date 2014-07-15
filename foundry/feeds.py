from collections import namedtuple

from PIL import Image

from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils import feedgenerator
from django.contrib.sites.models import get_current_site

from jmbo.models import ModelBase

from foundry.models import Listing, Page


class ListingFeed(Feed):
    """Feed for items in a listing"""

    feed_type = feedgenerator.Rss201rev2Feed
    description = ""

    def get_object(self, request, slug):
        self.request = request
        return get_object_or_404(Listing, slug=slug)

    def title(self, obj):
        return obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def items(self, obj):
        if not obj.enable_syndication:
            return ModelBase.objects.none()

        qs = obj.queryset()
        limit = obj.items_per_page or 10
        return qs[:limit]

    def get_image_info(self, item):
        # Cache image attributes on item to avoid multiple calls to load image
        cached = getattr(item, '_image_info', None)
        if cached is not None:
            return cached
        info = namedtuple('Info', ['url', 'length', 'mime_type'])('', 0, '')
        if item.image:
            blob = None
            try:
                blob = Image.open(item.image.path)
            except IOError:
                pass
            if blob:
                info = feedgenerator.Enclosure(
                    self.request.build_absolute_uri(item.image_detail_url),
                    len(blob.tobytes()),
                    'image/%s' % blob.format.lower()
                )
        setattr(item, '_image_info', info)
        return info

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_enclosure_url(self, item):
        return self.get_image_info(item).url

    def item_enclosure_length(self, item):
        return self.get_image_info(item).length

    def item_enclosure_mime_type(self, item):
        return self.get_image_info(item).mime_type


listing_feed = ListingFeed()
