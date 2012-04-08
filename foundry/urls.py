from django.conf.urls.defaults import patterns, url, include
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.contrib.auth.decorators import login_required

from preferences import preferences

from foundry.models import Page
from foundry import views, forms

admin.autodiscover()

try:
    import object_tools
    object_tools.autodiscover()
except ImportError:
    pass

urlpatterns = patterns('',    
    # Pre-empt url call since we want to disable view modifiers for gallery.
    url(r'^gallery/list/$', 'gallery.views.object_list', name='gallery_object_list'),
    url(
        r'^gallery/(?P<slug>[\w-]+)/$', 
        'gallery.views.object_detail', 
        {'view_modifier': []}, 
        name='gallery_object_detail'
    ),

    (r'^gallery/', include('gallery.urls')),
    (r'^googlesearch/', include('googlesearch.urls')),
    (r'^music/', include('music.urls')),
    (r'^jmbo/', include('jmbo.urls')),  # todo: paster makes this r'^$ which does not work
    (r'^chart/', include('chart.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
#    (r'^richcomments/', include('richcomments.urls')), # re-evaluate this product. It needs to degrade to non-ajax as well.
    (r'^likes/', include('likes.urls')),
    (r'^object-tools/', include(object_tools.tools.urls)),
    (r'^show/', include('show.urls')),
    (r'^event/', include('event.urls')),
    (r'^competition/', include('competition.urls')),
    (r'^ckeditor/', include('ckeditor.urls')),
    (r'^contact/', include('contact.urls')),
    (r'^post/', include('post.urls')),	# todo: add to paster
    (r'^poll/', include('poll.urls')),	# todo: add to paster
    (r'^simple-autocomplete/', include('simple_autocomplete.urls')),
    (r'^jmbo-analytics/', include('jmbo_analytics.urls')),

    (r'^admin/', include(admin.site.urls)),

    url(
        r'^$',
        'django.views.generic.simple.direct_to_template',
        {
            'template':'base.html', 
        },
        name='home'
    ),
    url(
        r'^logo/$',
        'django.views.generic.simple.direct_to_template',
        {
            'template':'foundry/logo.html', 
        },
        name='logo'
    ),
    url(
        r'^header/$',
        'django.views.generic.simple.direct_to_template',
        {
            'template':'foundry/inclusion_tags/header.html', 
        },
        name='header'
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
    # Pre-empt password reset so we can use custom form
    (
        r'^auth/password_reset/$', 
        'django.contrib.auth.views.password_reset', 
        {
            'password_reset_form': forms.PasswordResetForm,
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

    # Listing
    url(
        r'^listing/(?P<slug>[\w-]+)/$',
        'foundry.views.listing_detail',
        {},
        name='listing-detail'
    ),
    
    # My Profile
    
    url(r'^my-profile/update/$',
        login_required(views.UpdateProfile.as_view(form_class=forms.ProfileUpdateForm,
                                                   template_name='foundry/update_profile.html')),
        name='update-profile'
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
        'django.views.generic.simple.direct_to_template',
        {
            'template':'foundry/lorem_ipsum.html', 
        },
        name='lorem-ipsum'
    ),

    # Search
    url(
        r'^search/$',
        'foundry.views.search',
        {},
        name='search'
    ),

    # Comment reply form in case of no javascript
    url(
        r'^comment-reply-form/$',
        'foundry.views.comment_reply_form',
        {},
        name='comment-reply-form'
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
        'foundry.views.blogpost_object_list', 
        {'limit': 300},
        name='blogpost_object_list'
    ),
    
    # Blogpost detail
    url(
        r'^blogpost/(?P<slug>[\w-]+)/$', 
        'foundry.views.blogpost_object_detail', 
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

    # User activity
    url(
        r'^user-activity/$', 
        login_required(views.UserActivityView.as_view(template_name='foundry/user_activity.html')),
        name='user_activity'
    ),

    # User detail page
    url(
        r'^users/(?P<username>[\w-]+)/$', 
        'foundry.views.user_detail', 
        {},
        name='user-detail'
    ),

    # Member detail page
    url(r'^members/(?P<username>[\w-]+)/$', 
        views.MemberDetail.as_view(form_class=forms.CreateDirectMessage,
                                   template_name='foundry/member_detail.html'), 
        name='member-detail'
    ),
    
    # Messaging
    url(r'^inbox/$',
        login_required(views.Inbox.as_view(template_name='foundry/inbox.html')),
        name='inbox'
    ),
    url(r'^message/send/$',
        login_required(views.SendMessage.as_view(form_class=forms.SendDirectMessage,
                                                 template_name='foundry/message_send.html')),
        name='message-send'
    ),
    url(r'^message/(?P<pk>\d+)/view/$',
        login_required(views.ViewMessage.as_view(template_name='foundry/message_view.html')),
        name='message-view'
    ),
    url(r'^message/(?P<pk>\d+)/reply/$',
        login_required(views.ReplyToMessage.as_view(form_class=forms.ReplyDirectMessage,
                                                    template_name='foundry/message_reply.html')),
        name='message-reply'
    ),
    
    url(r'^my_badges/$',
        login_required(views.MyBadges.as_view(template_name='foundry/my_badges.html')),
        name='my-badges'
    ),

    # Coming soon
    url(
        r'^coming-soon/$',
        'django.views.generic.simple.direct_to_template',
        {
            'template':'foundry/coming_soon.html', 
        },
        name='coming-soon'
    ),
    url(
        r'^fetch-new-comments-ajax/(?P<content_type_id>\d+)/(?P<oid>\d+)/(?P<last_comment_id>\d+)/$',
        'foundry.views.fetch_new_comments_ajax',
        {},
        name='fetch-new-comments-ajax'
    ),

    # Friend request
    url(
        r'^friend-request/(?P<member_id>\d+)/$',
        login_required(views.friend_request),
        {},
        name='friend-request'
    ),

    # My friends
    url(
        r'^my-friends/$',
        login_required(views.my_friends),
        {'template_name':'foundry/my_friends.html'},
        name='my-friends'
    ),

    # My friend requests
    url(
        r'^my-friend-requests/$',
        login_required(views.my_friend_requests),
        {'template_name':'foundry/my_friend_requests.html'},
        name='my-friend-requests'
    ),

    # Accept friend request
    url(
        r'^accept-friend-request/(?P<memberfriend_id>\d+)/$',
        login_required(views.accept_friend_request),
        {},
        name='accept-friend-request'
    ),

    # De-friend a member
    url(
        r'^de-friend/(?P<member_id>\d+)/$',
        login_required(views.de_friend),
        {},
        name='de-friend'
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
        'django.views.generic.list_detail.object_list',
        {'queryset':Page.permitted.all().order_by('title')},
        'page-list'
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

)

urlpatterns += staticfiles_urlpatterns()

handler500 = 'foundry.views.server_error'

if settings.DEBUG:
    urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
