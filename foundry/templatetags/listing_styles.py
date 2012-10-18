from django.template.loader import render_to_string
from django.utils.importlib import import_module

from jmbo.models import ModelBase


class AbstractBaseStyle(object):

    def __init__(self, listing):
        self.listing = listing
    
    def get_queryset(self, request=None):
        return self.listing.queryset(request)

    def get_pinned_queryset(self):
        # Check for pinned_queryset. It can be missing since listings can be 
        # called via the {% listing %} tag. The resulting proxy listing object 
        # does not neccessarily have the property.
        return getattr(self.listing, 'pinned_queryset', ModelBase.objects.none())
       
    def get_context_data(self, context, as_tile=False):
        request = context['request']

        context['object_list'] = self.get_queryset(request)
        context['pinned_list'] = self.get_pinned_queryset()
        context['listing'] = self.listing
        context['items_per_page'] = self.listing.items_per_page or 100
        context['view_modifier'] = None
        view_modifier = getattr(self.listing, 'view_modifier', None)
        if view_modifier:
            mod, attr = view_modifier.rsplit('.', 1)
            context['view_modifier'] = getattr(import_module(mod), attr)(request)

        context['display_title'] = True
        if as_tile and not self.listing.display_title_tiled:
            context['display_title'] = False       
        
        return context

    def render(self, context, as_tile=False):
        context.push()
        result = render_to_string(self.template_name, self.get_context_data(context, as_tile=as_tile))
        context.pop()
        return result


class Horizontal(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_horizontal.html'


class Vertical(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_vertical.html'


class Promo(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_promo.html'


class VerticalThumbnail(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_vertical_thumbnail.html'


class Widget(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_widget.html'
