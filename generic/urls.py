from django.conf.urls.defaults import patterns, url, include
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout
from django.utils.translation import ugettext_lazy as _

from preferences import preferences

from generic.forms import LoginForm, PasswordResetForm
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
        r'^join-finish/$',
        'generic.views.join_finish',
        {},
        name='join-finish',
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
    # Pre-empt password reset so we can use custom form
    (
        r'^auth/password_reset/$', 
        'django.contrib.auth.views.password_reset', 
        {
            'password_reset_form':PasswordResetForm,
        }
    ),
    (r'^auth/', include('django.contrib.auth.urls')),

    # Pages defined in preferences
    url(
        r'^about-us/$',
        'django.views.generic.simple.direct_to_template',
        {
            'template':'generic/static_page.html', 
            'extra_context':{'content':lambda:preferences.GeneralPreferences.about_us, 'title':_("About us")}
        },
        name='about-us'
    ),
    url(
        r'^terms-and-conditions/$',
        'django.views.generic.simple.direct_to_template',
        {
            'template':'generic/static_page.html', 
            'extra_context':{'content':lambda:preferences.GeneralPreferences.terms_and_conditions, 'title':_("Terms and conditions")}
        },
        name='terms-and-conditions'
    ),
    url(
        r'^privacy-policy/$',
        'django.views.generic.simple.direct_to_template',
        {
            'template':'generic/static_page.html', 
            'extra_context':{'content':lambda:preferences.GeneralPreferences.privacy_policy, 'title':_("Privacy policy")}
        },
        name='privacy-policy'
    ),

)
