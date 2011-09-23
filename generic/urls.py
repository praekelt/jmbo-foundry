from django.conf.urls.defaults import patterns, url, include
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout

from generic.forms import LoginForm

urlpatterns = patterns(
    'generic.views',
    url(r'^$', TemplateView.as_view(template_name="generic/home.html"), \
            name='home'),

    # Join, login, password reset            
    url(
        r'^join/$',
        'join',
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
