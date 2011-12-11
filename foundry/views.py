from django.conf import settings
from django.contrib.auth import authenticate, login, get_backends
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from category.models import Category
from jmbo.models import ModelBase

from foundry.models import Listing, Page
from foundry.forms import JoinForm, JoinFinishForm, AgeGatewayForm, TestForm, \
    SearchForm


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
            return obj.as_leaf_class().get_absolute_url()
        else:
            return self


def join(request):
    """Surface join form"""
    if request.method == 'POST':
        form = JoinForm(request.POST, request.FILES) 
        if form.is_valid():
            member = form.save()
            backend = get_backends()[0]
            member.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, member)            
            return HttpResponseRedirect(reverse('join-finish'))
    else:
        form = JoinForm() 

    extra = dict(form=form)
    return render_to_response('foundry/join.html', extra, context_instance=RequestContext(request))


@login_required
def join_finish(request):
    """Surface join finish form"""
    if request.method == 'POST':
        form = JoinFinishForm(request.POST, request.FILES, instance=request.user) 
        if form.is_valid():
            member = form.save()
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = JoinFinishForm(instance=request.user) 

    extra = dict(form=form)
    return render_to_response('foundry/join_finish.html', extra, context_instance=RequestContext(request))


class CategoryObjectDetailView(DetailView):
    model = ModelBase
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug__iexact=self.kwargs['category_slug'])
        return super(CategoryObjectDetailView, self).get_queryset()

    def get_template_names(self):
        # todo: explain name resolution in documentation
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
        return ModelBase.permitted.filter(Q(primary_category=self.category)|Q(categories=self.category)).exclude(pin__category=self.category)
        
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


def age_gateway(request):
    """Surface age gateway form"""
    if request.method == 'POST':
        form = AgeGatewayForm(request.POST) 
        if form.is_valid():
            # save returns a response
            return form.save(request)
    else:
        form = AgeGatewayForm() 

    extra = dict(form=form)
    return render_to_response('foundry/age_gateway.html', extra, context_instance=RequestContext(request))


def listing_detail(request, slug):
    """Render a page by iterating over rows, columns and tiles."""
    listing = get_object_or_404(Listing, slug=slug)
    extra = {}
    extra['object'] = listing
    return render_to_response('foundry/listing_detail.html', extra, context_instance=RequestContext(request))


def page_detail(request, slug):
    """Render a page by iterating over rows, columns and tiles."""
    page = get_object_or_404(Page, slug=slug)
    extra = {}
    extra['object'] = page
    return render_to_response('foundry/page_detail.html', extra, context_instance=RequestContext(request))


# todo: caching
def home_resolver(request):
    """If there is a Page that is set to be home then render and return, else
    render and return home.html."""
    pages = Page.objects.filter(is_homepage=True)
    if pages.count():
        page = pages[0]
        extra = {}
        extra['object'] = page
        return render_to_response('foundry/page_detail.html', extra, context_instance=RequestContext(request))

    return render_to_response('foundry/home.html', {}, context_instance=RequestContext(request))


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST) 
        if form.is_valid():
            return HttpResponseRedirect('/')
    else:
        form = SearchForm() 

    extra = dict(form=form)
    return render_to_response('foundry/search.html', extra, context_instance=RequestContext(request))


# Views for testing
def test_plain_response(request):
    if request.method == 'POST':
        form = TestForm(request.POST) 
        if form.is_valid():
            return HttpResponse('Success')
    else:
        form = TestForm() 

    extra = dict(title='Plain', form=form)
    return render_to_response('foundry/test_form.html', extra, context_instance=RequestContext(request))


def test_redirect(request):
    if request.method == 'POST':
        form = TestForm(request.POST) 
        if form.is_valid():
            return HttpResponseRedirect('/lorem-ipsum')
    else:
        form = TestForm() 

    extra = dict(title='Redirect', form=form)
    return render_to_response('foundry/test_form.html', extra, context_instance=RequestContext(request))

