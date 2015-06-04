from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView

from preferences import preferences
from jmbo.urls import v1_api
# Trivial imports so resource registration works
import post.urls

from foundry.models import Page
from foundry import views, forms
from foundry.api import ListingResource, LinkResource, NavbarResource, \
    MenuResource, PageResource, BlogPostResource


admin.autodiscover()

try:
    import object_tools
    object_tools.autodiscover()
except ImportError:
    pass

v1_api.register(ListingResource())
v1_api.register(LinkResource())
v1_api.register(NavbarResource())
v1_api.register(MenuResource())
v1_api.register(PageResource())
v1_api.register(BlogPostResource())


urlpatterns = patterns('',
    # Pre-empt url call for comment post
    url(
        r'^comments/post/$',
        'foundry.views.post_comment',
        {},
        name='comments-post-comment'
    ),

    (r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico', permanent=False)),

    (r'^googlesearch/', include('googlesearch.urls')),
    (r'^jmbo/', include('jmbo.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^likes/', include('likes.urls')),
    (r'^object-tools/', include(object_tools.tools.urls)),
    (r'^ckeditor/', include('ckeditor.urls')),
    (r'^contact/', include('contact.urls')),
    (r'^post/', include('post.urls')),
    (r'^simple-autocomplete/', include('simple_autocomplete.urls')),
    (r'^jmbo-analytics/', include('jmbo_analytics.urls')),
    (r'^api/', include(v1_api.urls)),
    url(r'social-auth', include('social_auth.urls')),

    (r'^admin/', include(admin.site.urls)),

    url(
        r'^$',
        TemplateView.as_view(template_name='base.html'),
        name='home'
    ),
    url(
        r'^logo/$',
        TemplateView.as_view(template_name='foundry/logo.html'),
        name='logo'
    ),
    url(
        r'^header/$',
        TemplateView.as_view(template_name='foundry/inclusion_tags/header.html'),
        name='header'
    ),
    url(
        r'^footer/$',
        TemplateView.as_view(template_name='foundry/inclusion_tags/footer.html'),
        name='footer'
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
    (r'^auth/', include('django.contrib.auth.urls')),
    url(
        r'^login/$',
        'django.contrib.auth.views.login',
        {'authentication_form': forms.LoginForm},
        name='login',
    ),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page':'/'},
        name='logout',
    ),
    # Password reset with custom form
    url(
        r'^password_reset/$',
        'django.contrib.auth.views.password_reset',
        {
            'password_reset_form': forms.PasswordResetForm,
        },
        name='password_reset',
    ),

    # Pages defined in preferences
    url(
        r'^about-us/$',
        views.StaticView.as_view(
            content=lambda:preferences.GeneralPreferences.about_us,
            title=_("About us")
        ),
        name='about-us'
    ),
    url(
        r'^terms-and-conditions/$',
        views.StaticView.as_view(
            content=lambda:preferences.GeneralPreferences.terms_and_conditions,
            title=_("Terms and conditions")
        ),
        name='terms-and-conditions'
    ),
    url(
        r'^privacy-policy/$',
        views.StaticView.as_view(
            content=lambda:preferences.GeneralPreferences.privacy_policy,
            title=_("Privacy policy")
        ),
        name='privacy-policy'
    ),

    # Age gateway
    url(
        r'^age-gateway/$',
        'foundry.views.age_gateway',
        {},
        name='age-gateway',
    ),

    # Listing
    url(
        r'^listing/(?P<slug>[\w-]+)/$',
        'foundry.views.listing_detail',
        {},
        name='listing-detail'
    ),

    # Listing feed
    url(
        r'^listing/(?P<slug>[\w-]+)/feed/$',
        'foundry.feeds.listing_feed',
        {},
        name='listing-feed'
    ),

    # Edit profile
    url(r'^edit-profile/$',
        login_required(
            views.EditProfile.as_view(
                form_class=forms.EditProfileForm,
                template_name='foundry/edit_profile.html'
            )
        ),
        name='edit-profile'
    ),

    # Complete profile
    url(r'^complete-profile/$',
        login_required(
            views.EditProfile.as_view(
                form_class=forms.EditProfileForm,
                template_name='foundry/complete_profile.html'
            )
        ),
        name='complete-profile'
    ),

    # Page detail
    url(
        r'^page/(?P<slug>[\w-]+)/$',
        'foundry.views.page_detail',
        {},
        name='page-detail'
    ),

    # Lorem ipsum
    url(
        r'^lorem-ipsum/$',
        TemplateView.as_view(template_name='foundry/lorem_ipsum.html'),
        name='lorem-ipsum'
    ),

    # Search
    url(
        r'^search/$',
        'foundry.views.search',
        {},
        name='search'
    ),

    # Search results
    url(
        r'^search-results/$',
        'foundry.views.search_results',
        {},
        name='search-results'
    ),

    # Comment reply form in case of no javascript
    url(
        r'^comment-reply-form/$',
        'foundry.views.comment_reply_form',
        {},
        name='comment-reply-form'
    ),

    # Report comment
    url(
        r'^report-comment/(?P<comment_id>\d+)/$',
        'foundry.views.report_comment',
        {},
        name='report-comment'
    ),

    # Chatroom detail
    url(
        r'^chatroom/(?P<slug>[\w-]+)/$',
        'foundry.views.chatroom_detail',
        {},
        name='chatroom-detail'
    ),

    # Create blogpost
    url(
        r'^create-blogpost/$',
        'foundry.views.create_blogpost',
        {},
        name='create-blogpost',
    ),

    # Blogpost list
    url(
        r'^blogposts/$',
        views.BlogPostObjectList.as_view(),
        {'limit': 300},
        name='blogpost_object_list'
    ),

    # Blogpost detail
    url(
        r'^blogpost/(?P<slug>[\w-]+)/$',
        views.BlogPostObjectDetail.as_view(),
        {},
        name='blogpost_object_detail'
    ),

    # Member notifications
    url(
        r'^member-notifications/$',
        login_required(views.member_notifications),
        {},
        name='member-notifications'
    ),

    # User detail page
    url(
        r'^users/(?P<username>[=@\.\w-]+)/$',
        'foundry.views.user_detail',
        {},
        name='user-detail'
    ),

    # Coming soon
    url(
        r'^coming-soon/$',
        TemplateView.as_view(template_name='foundry/coming_soon.html'),
        name='coming-soon'
    ),

    # Load new comments
    url(
        r'^fetch-new-comments-ajax/(?P<content_type_id>\d+)/(?P<oid>\d+)/(?P<last_comment_id>\d+)/$',
        'foundry.views.fetch_new_comments_ajax',
        {},
        name='fetch-new-comments-ajax'
    ),

    # Test views
    url(
        r'^test-plain-response/$',
        'foundry.views.test_plain_response',
        {},
        name='test-plain-response'
    ),
    url(
        r'^test-redirect/$',
        'foundry.views.test_redirect',
        {},
        name='test-redirect'
    ),
    url(
        r'^pages/$',
        DetailView.as_view(),
        {'queryset':Page.permitted.all().order_by('title')},
        'page-list'
    ),

    # Member detail page
    url(
        r'^members/(?P<username>[\w-]+)/$',
        'foundry.views.member_detail',
        {},
        name='member-detail'
    ),

    # Admin
    url(
        r'^admin-row-create-ajax/$',
        'foundry.admin_views.row_create_ajax',
        {},
        name='admin-row-create-ajax',
    ),
    url(
        r'^admin-column-create-ajax/$',
        'foundry.admin_views.column_create_ajax',
        {},
        name='admin-column-create-ajax',
    ),
    url(
        r'^admin-tile-create-ajax/$',
        'foundry.admin_views.tile_create_ajax',
        {},
        name='admin-tile-create-ajax',
    ),
    url(
        r'^admin-row-edit-ajax/$',
        'foundry.admin_views.row_edit_ajax',
        {},
        name='admin-row-edit-ajax',
    ),
    url(
        r'^admin-column-edit-ajax/$',
        'foundry.admin_views.column_edit_ajax',
        {},
        name='admin-column-edit-ajax',
    ),
    url(
        r'^admin-tile-edit-ajax/$',
        'foundry.admin_views.tile_edit_ajax',
        {},
        name='admin-tile-edit-ajax',
    ),
    url(
        r'^admin-row-delete-ajax/$',
        'foundry.admin_views.row_delete_ajax',
        {},
        name='admin-row-delete-ajax',
    ),
    url(
        r'^admin-column-delete-ajax/$',
        'foundry.admin_views.column_delete_ajax',
        {},
        name='admin-column-delete-ajax',
    ),
    url(
        r'^admin-tile-delete-ajax/$',
        'foundry.admin_views.tile_delete_ajax',
        {},
        name='admin-tile-delete-ajax',
    ),
    url(
        r'^admin-persist-sort-ajax/$',
        'foundry.admin_views.persist_sort_ajax',
        {},
        name='admin-persist-sort-ajax',
    ),
    url(
        r'^admin-remove-comment/(?P<comment_id>\d+)/$',
        'foundry.admin_views.remove_comment',
        {},
        name='admin-remove-comment'
    ),
    url(
        r'^admin-allow-comment/(?P<comment_id>\d+)/$',
        'foundry.admin_views.allow_comment',
        {},
        name='admin-allow-comment'
    ),

)

# Praekelt maintained Jmbo packages which are optional
if "banner" in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^banner/', include('banner.urls')))
if "chart" in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^chart/', include('chart.urls')))
if "competition" in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^competition/', include('competition.urls')))
if "downloads" in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^downloads/', include('downloads.urls')))
if "friends" in settings.INSTALLED_APPS:
    # Friends has a fancy member detail page and needs to resolve first
    urlpatterns.insert(1, url(r'^friends/', include('friends.urls')))
if "gallery" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^gallery/', include('gallery.urls')),
        (r'^admin/', include('gallery.admin_urls')),
    )
if "jmbo_calendar" in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^calendar/', include('jmbo_calendar.urls')))
if "jmbo_twitter" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^jmbo_twitter', include('jmbo_twitter.urls')),
        (r'^admin/', include('jmbo_twitter.admin_urls')),
)
if "music" in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^music/', include('music.urls')))
if "poll" in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^poll/', include('poll.urls')))
if "show" in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^show/', include('show.urls')))
if "jmbo_sitemap" in settings.INSTALLED_APPS:
    from jmbo_sitemap import sitemaps
    from jmbo_sitemap.views import sitemap, SitemapHTMLView
    urlpatterns += patterns(
        '',
        # Unidentified issue with Jmbo URLPatternItem class means
        # (r'^', include('jmbo_sitemap.urls')) causes error. Use a workaround.
        url(
            r'^sitemap\.xml$',
            sitemap,
            {'sitemaps': sitemaps},
            name='sitemap'
        ),
        url(
            r'^sitemap/$',
            SitemapHTMLView.as_view(),
            name='html-sitemap'
        ),
    )

urlpatterns += staticfiles_urlpatterns()

# Flatpages must be last
urlpatterns += patterns('', ('r^/', include('django.contrib.flatpages.urls')))

handler500 = 'foundry.views.server_error'

if settings.DEBUG:
    urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
