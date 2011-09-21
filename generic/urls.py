from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    'generic.views',
    url(r'^$', TemplateView.as_view(template_name="generic/home.html"), \
            name='home'),
)
