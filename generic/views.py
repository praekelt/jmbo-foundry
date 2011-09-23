from django.conf import settings
from django.contrib.auth import authenticate, login, get_backends
from django.http import HttpResponseRedirect 
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from generic.forms import JoinForm

from category.models import Category
from jmbo.models import ModelBase

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
    pass


class CategoryObjectListView(ListView):
    paginate_by = 5

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug__iexact=self.kwargs['category_slug'])
        return ModelBase.permitted.filter(categories=self.category).order_by('-created')
    
    def get_template_names(self):
        return ['category/%s_list.html' % self.category.slug, 'category/list.html'] + super(CategoryObjectListView, self).get_template_names()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CategoryObjectListView, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context

