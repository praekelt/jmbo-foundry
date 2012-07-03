from django.template.loader import render_to_string


class AbstractBaseStyle(object):

    def __init__(self, listing):
        self.listing = listing
    
    def get_queryset(self):
        return self.listing.queryset
            
    def get_context_data(self, context, as_tile=False):
        context['object_list'] = self.get_queryset()
        context['listing'] = self.listing
        context['items_per_page'] = self.listing.items_per_page or 100
        if getattr(context['request'], 'page', 0) < 0:
            setattr(context['request'], 'page', 1)

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
