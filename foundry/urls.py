from django.conf.urls.defaults import patterns, url, include
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from preferences import preferences

from foundry.forms import LoginForm, PasswordResetForm
from foundry.views import CategoryObjectDetailView, CategoryObjectListView

admin.autodiscover()

try:
    import object_tools
    object_tools.autodiscover()
except ImportError:
    pass

urlpatterns = patterns('',
    (r'^gallery/', include('gallery.urls')),
    (r'^googlesearch/', include('googlesearch.urls')),
    (r'^music/', include('music.urls')),
    (r'^$', include('jmbo.urls')),
    (r'^chart/', include('chart.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^richcomments/', include('richcomments.urls')),
    (r'^likes/', include('likes.urls')),
    (r'^object-tools/', include(object_tools.tools.urls)),
    (r'^show/', include('show.urls')),
    (r'^event/', include('event.urls')),
    (r'^competition/', include('competition.urls')),
    (r'^ckeditor/', include('ckeditor.urls')),
    (r'^contact/', include('contact.urls')),
    (r'^post/', include('post.urls')),	# todo: add to paster
    (r'^simple-autocomplete/', include('simple_autocomplete.urls')),

    (r'^admin/', include(admin.site.urls)),

    url(
        r'^$',
        TemplateView.as_view(template_name="foundry/home.html"),
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
        'foundry.views.join',
        {},
        name='join',
    ),
    url(
        r'^join-finish/$',
        'foundry.views.join_finish',
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
            'template':'foundry/static_page.html', 
            'extra_context':{'content':lambda:preferences.GeneralPreferences.about_us, 'title':_("About us")}
        },
        name='about-us'
    ),
    url(
        r'^terms-and-conditions/$',
        'django.views.generic.simple.direct_to_template',
        {
            'template':'foundry/static_page.html', 
            'extra_context':{'content':lambda:preferences.GeneralPreferences.terms_and_conditions, 'title':_("Terms and conditions")}
        },
        name='terms-and-conditions'
    ),
    url(
        r'^privacy-policy/$',
        'django.views.generic.simple.direct_to_template',
        {
            'template':'foundry/static_page.html', 
            'extra_context':{'content':lambda:preferences.GeneralPreferences.privacy_policy, 'title':_("Privacy policy")}
        },
        name='privacy-policy'
    ),

    # Age gateway
    url(
        r'^age-gateway/$',
        'foundry.views.age_gateway',
        {},
        name='age-gateway',
    ),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
