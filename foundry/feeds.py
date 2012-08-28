from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404

from foundry.models import Listing, Page


class ListingFeed(Feed):
    """Feed for items in a listing"""

    description = ""

    def get_object(self, request, slug):
        return get_object_or_404(Listing, slug=slug)

    def title(self, obj):
        return obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def items(self, obj):
        qs = obj.queryset()
        limit = obj.items_per_page or 10
        return qs[:limit]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description


listing_feed = ListingFeed()
