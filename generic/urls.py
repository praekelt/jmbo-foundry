from django.conf.urls.defaults import patterns, url, include
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout

from generic.forms import LoginForm
from generic.views import CategoryObjectDetailView, CategoryObjectListView

urlpatterns = patterns('',
    url(
        r'^$',
        TemplateView.as_view(template_name="generic/home.html"),
        name='home'
    ),
    url(
        r'^category/(?P<category_slug>[\w-]+)/$',
        CategoryObjectListView.as_view(),
        name='category_object_list'
    ),
    url(
        r'^category/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$',
        CategoryObjectDetailView.as_view(),
        name='category_object_detail'
    ),
    # Join, login, password reset            
    url(
        r'^join/$',
        'generic.views.join',
        {},
        name='join',
    ),
    url(
        r'^login/$',
        login,
        {'authentication_form':LoginForm},
        name='login',
    ),
    url(
        r'^logout/$',
        logout,
        {},
        name='logout',
    ),
    (r'^auth/', include('django.contrib.auth.urls')),
)
