from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView
from django.contrib.auth.views import login

from generic.forms import LoginForm

urlpatterns = patterns(
    'generic.views',
    url(r'^$', TemplateView.as_view(template_name="generic/home.html"), \
            name='home'),

    url(
        r'^login/$',
        login,
        {'authentication_form':LoginForm},
        name='login',
    ),

)
