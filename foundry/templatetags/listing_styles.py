from django.template.loader import render_to_string

from jmbo import models

class AbstractBaseStyle(object):

    def __init__(self, listing):
        self.listing = listing
    
    def get_queryset(self):
        queryset = self.listing.content.all()
        if not queryset.exists():
            queryset = models.ModelBase.permitted.all()
            if self.listing.category:
                queryset = queryset.filter(categories=self.listing.category)
        return queryset[:self.listing.count]
    
    def get_url_callable(self, *args, **kwargs):
        # Must put the import here to avoid circular import error
        from foundry import views
        return views.CategoryURL(category=self.listing.category)
    
    def get_context_data(self, *args, **kwargs):
        context = {}
        context['object_list'] = self.get_queryset()
        context['listing'] = self.listing
        context['url_callable'] = self.get_url_callable()
        return context

    def render(self, context):
        return render_to_string(self.template_name, self.get_context_data(context))


class Horizontal(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_horizontal.html'


class Vertical(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_vertical.html'


class Promo(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_promo.html'


class VerticalThumbnail(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_vertical_thumbnail.html'

