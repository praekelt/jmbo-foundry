from django.template.loader import render_to_string

from jmbo import models

class Promo(object):
    template_name = 'foundry/inclusion_tags/page_block_promo.html'

    def __init__(self, page_block):
        self.page_block = page_block
    
    def get_queryset(self):
        queryset = self.page_block.content.all()
        if not queryset:
            queryset = models.ModelBase.permitted.all()
            if self.page_block.category:
                queryset = queryset.filter(categories=self.page_block.category)
        return queryset[:self.page_block.count]
    
    def get_url_callable(self, *args, **kwargs):
        # Must put the import here to avoid circular import error
        from foundry import views
        return views.CategoryURL(category=self.page_block.category)
    
    def get_context_data(self, *args, **kwargs):
        context = {}
        context['object_list'] = self.get_queryset()
        context['page_block'] = self.page_block
        context['url_callable'] = self.get_url_callable()
        return context

    def render(self, context):
        return render_to_string(self.template_name, self.get_context_data(context))

class Listing(Promo):
    template_name = 'foundry/inclusion_tags/page_block_listing.html'

