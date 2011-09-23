from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView

from generic.views import CategoryObjectDetailView, CategoryObjectListView

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="generic/home.html"), \
            name='home'),
    url(r'^category/(?P<category_slug>[\w-]+)/$', \
            CategoryObjectListView.as_view(), name='category_object_list'),
    url(r'^category/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$', \
            CategoryObjectDetailView.as_view(), name='category_object_detail'),
)
