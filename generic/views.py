from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from category.models import Category
from jmbo.models import ModelBase


class CategoryObjectDetailView(DetailView):
    pass


class CategoryObjectListView(ListView):
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug__iexact=self.kwargs['category_slug'])
        return ModelBase.permitted.filter(categories=self.category)
    
    def get_template_names(self):
        return ['category/%s_list.html' % self.category.slug] + super(CategoryObjectListView, self).get_template_names()
