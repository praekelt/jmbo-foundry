from django.conf import settings
from django.contrib.auth import authenticate, login, get_backends
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect 
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from generic.forms import JoinForm

from category.models import Category
from jmbo.models import ModelBase

class CategoryURL(object):

    def __init__(self, category=None):
        self.category = category

    def __call__(self, obj=None):
        if self.category and obj:
            return reverse(
                'category_object_detail',
                kwargs={'category_slug': self.category.slug, 'slug': obj.slug}
            )
        elif obj:
            return obj.get_absolute_url()
        else:
            return self

def join(request):
    """Surface join form"""
    if request.method == 'POST':
        form = JoinForm(request.POST, request.FILES) 
        if form.is_valid():
            user = form.save()
            backend = get_backends()[0]
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, user)            
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = JoinForm() 

    extra = dict(form=form)
    return render_to_response('generic/join.html', extra, context_instance=RequestContext(request))

class CategoryObjectDetailView(DetailView):
    model = ModelBase
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug__iexact=self.kwargs['category_slug'])
        return super(CategoryObjectDetailView, self).get_queryset()

    def get_template_names(self):
        return ['category/%s_detail.html' % self.category.slug, 'category/detail.html'] + super(CategoryObjectDetailView, self).get_template_names()
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CategoryObjectDetailView, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['object'] = context['object'].as_leaf_class()
        return context

class CategoryObjectListView(ListView):
    paginate_by = 5

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug__iexact=self.kwargs['category_slug'])
        return ModelBase.permitted.filter(categories=self.category).exclude(pin__category=self.category)
        
    def get_template_names(self):
        return ['category/%s_list.html' % self.category.slug, 'category/list.html'] + super(CategoryObjectListView, self).get_template_names()
    
    def get_url_callable(self, *args, **kwargs):
        return CategoryURL(category=self.category)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CategoryObjectListView, self).get_context_data(**kwargs)
        context['pinned_object_list'] = ModelBase.permitted.filter(pin__category=self.category).order_by('-created')
        context['category'] = self.category
        context['url_callable'] = self.get_url_callable()
        return context
