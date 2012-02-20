from django.template.loader import render_to_string

from jmbo import models


class AbstractBaseStyle(object):

    def __init__(self, listing):
        self.listing = listing
    
    def get_queryset(self):
        # todo: performance investigation required
        queryset = self.listing.content.all()
        if not queryset.exists():
            queryset = models.ModelBase.permitted.all()
            if self.listing.content_type.exists():
                queryset = queryset.filter(content_type__in=self.listing.content_type.all())
            elif self.listing.category:
                # Import here since there is code that inspects this module and
                # it picks up Q. todo: fix
                from django.db.models import Q
                queryset = queryset.filter(Q(primary_category=self.listing.category)|Q(categories=self.listing.category))
        if self.listing.count:
            queryset = queryset[:self.listing.count]
        return queryset
    
    def get_url_callable(self, *args, **kwargs):
        # Must put the import here to avoid circular import error
        from jmbo import views
        return views.CategoryURL(category=self.listing.category)
    
    def get_context_data(self, context):
        context['object_list'] = self.get_queryset()
        context['listing'] = self.listing
        context['url_callable'] = self.get_url_callable()
        context['items_per_page'] = self.listing.items_per_page or 100
        if getattr(context['request'], 'page', 0) < 0:
            setattr(context['request'], 'page', 1)
        return context

    def render(self, context):
        context.push()
        result = render_to_string(self.template_name, self.get_context_data(context))
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
