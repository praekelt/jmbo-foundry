import datetime
import random
import urllib

from django.conf import settings
from django.contrib.auth import authenticate, login, get_backends
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, \
    HttpResponseServerError
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.models import get_current_site
from django.template import Template
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import View, ListView
from django.utils.translation import ugettext_lazy as _, ugettext

from django_geckoboard.decorators import number_widget, funnel, text_widget, TEXT_NONE

from category.models import Category
from jmbo.models import ModelBase
from jmbo.generic.views import GenericObjectDetail, GenericObjectList
from jmbo.view_modifiers import DefaultViewModifier
from preferences import preferences

from foundry.models import Listing, Page, ChatRoom, BlogPost, Notification, \
    Member, UserAgent, FoundryComment
from foundry.forms import JoinForm, JoinFinishForm, AgeGatewayForm, TestForm, \
    SearchForm, CreateBlogPostForm

from activity import constants as activity_constants
from activity.models import UserActivity

from likes import views as likes_views
from likes.utils import can_vote

def join(request):
    """Surface join form"""
    show_age_gateway = preferences.GeneralPreferences.show_age_gateway \
        and not request.COOKIES.get('age_gateway_passed')
    if request.method == 'POST':
        form = JoinForm(request.POST, request.FILES, show_age_gateway=show_age_gateway) 
        if form.is_valid():
            member = form.save()
            backend = get_backends()[0]
            member.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, member)            
            response = HttpResponseRedirect(reverse('join-finish'))

            # Set cookie if age gateway applicable. Can't delegate to form :(
            if show_age_gateway:
                now = datetime.datetime.now()
                expires = now.replace(year=now.year+10)
                response.set_cookie('age_gateway_passed', value=1, expires=expires)

            msg = _("You have successfully signed up to the site.")
            messages.success(request, msg, fail_silently=True)

            return response

    else:
        form = JoinForm(show_age_gateway=show_age_gateway) 

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


def age_gateway(request):
    """Surface age gateway form"""
    if request.method == 'POST':
        form = AgeGatewayForm(request.POST) 
        if form.is_valid():
            # Method save returns a response
            return form.save(request)
    else:
        form = AgeGatewayForm() 

    extra = dict(form=form)
    return render_to_response('foundry/age_gateway.html', extra, context_instance=RequestContext(request))


def listing_detail(request, slug):
    """Render a page by iterating over rows, columns and tiles."""
    try:
        listing = Listing.permitted.get(slug=slug)
    except Listing.DoesNotExist:
        raise Http404('No listing matches the given query.')
    extra = {}
    extra['object'] = listing
    return render_to_response('foundry/listing_detail.html', extra, context_instance=RequestContext(request))


def page_detail(request, slug):
    """Render a page by iterating over rows, columns and tiles."""
    try:
        page = Page.permitted.get(slug=slug)
    except Page.DoesNotExist:
        raise Http404('No page matches the given query.')
    extra = {}
    extra['object'] = page
    return render_to_response('foundry/page_detail.html', extra, context_instance=RequestContext(request))


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST) 
        if form.is_valid():
            return HttpResponseRedirect('/')
    else:
        form = SearchForm() 

    extra = dict(form=form)
    return render_to_response('foundry/search.html', extra, context_instance=RequestContext(request))


def comment_reply_form(request):
    obj = ContentType.objects.get(
        id=request.GET['content_type_id']
    ).get_object_for_this_type(id=request.GET['oid'])
    extra = {'object': obj, 'next': request.GET['path_info']}
    return render_to_response('foundry/comment_reply_form.html', extra, context_instance=RequestContext(request))


def chatroom_detail(request, slug):    
    chatroom = get_object_or_404(ChatRoom, slug=slug)
    extra = {}
    extra['object'] = chatroom
    return render_to_response('foundry/chatroom_detail.html', extra, context_instance=RequestContext(request))


@login_required
def create_blogpost(request):
    if request.method == 'POST':
        form = CreateBlogPostForm(request.POST, user=request.user, site=get_current_site(request)) 
        if form.is_valid():
            instance = form.save()
            request.user.message_set.create(message=_("The blog post %s has been saved") % instance.title)
            return HttpResponseRedirect('/page/my-blogs/')
    else:
        form = CreateBlogPostForm(user=request.user, site=get_current_site(request)) 

    extra = dict(form=form)
    return render_to_response('foundry/create_blogpost.html', extra, context_instance=RequestContext(request))


class BlogPostObjectList(GenericObjectList):

    def get_queryset(self, *args, **kwargs):
        return BlogPost.permitted.all()

    def get_extra_context(self, *args, **kwargs):
        return {'title': _('Blog Posts')}

    def get_view_modifier(self, request, *args, **kwargs):
        return DefaultViewModifier(request, *args, **kwargs)

    def get_paginate_by(self, *args, **kwargs):
        return 10

blogpost_object_list = BlogPostObjectList()


class BlogPostObjectDetail(GenericObjectDetail):

    def get_queryset(self, *args, **kwargs):
        return BlogPost.permitted.all()

    def get_extra_context(self, *args, **kwargs):
        return {'title': 'Blog Posts'}

blogpost_object_detail = BlogPostObjectDetail()


class BlogsAll(ListView):
    
    def get_queryset(self):
        return BlogPost.permitted.all().order_by('-created')

    
class BlogsMine(ListView):
    
    def get_queryset(self):
        return BlogPost.permitted.filter(owner=self.request.user).order_by('-created')
    
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        if len(self.object_list) == 0:
            return HttpResponseRedirect(reverse('create-blogpost'))
        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)

    
class BlogsFriends(ListView):
    
    def get_queryset(self):
        try:
            _, friend_ids = self.request.user.member.get_friends_with_ids()
            return BlogPost.permitted.filter(owner__id__in=friend_ids).order_by('-created')
        except:
            return BlogPost.objects.none()

@login_required
def member_notifications(request):
    """Page listing notifications for authenticated member"""
    extra = {}
    extra['object_list'] = Notification.objects.filter(member=request.user).order_by('-created')
    return render_to_response('foundry/member_notifications.html', extra, context_instance=RequestContext(request))


def user_detail(request, username):
    # Check if user has a corresponding Member object. Use that if possible.
    try:
        obj = Member.objects.get(username=username)
        return HttpResponseRedirect(reverse('member-detail', args=[username]))
    except Member.DoesNotExist:
        obj = get_object_or_404(User, username=username)
        template = 'foundry/user_detail.html'

    extra = {}
    extra['object'] = obj
    return render_to_response(template, extra, context_instance=RequestContext(request))

def member_detail(request, username):
    obj = get_object_or_404(Member, username=username)
    extra = {}
    extra['object'] = obj
    return render_to_response('foundry/member_detail.html', extra, context_instance=RequestContext(request))

class EditProfile(UpdateView):
    
    def get_object(self):
        member = Member.objects.get(id=self.request.user.id)
        self.success_url = reverse('member-detail', args=[member.username])
        return member

    def form_valid(self, form):
        msg = _("Your profile has been updated.")
        messages.success(self.request, msg, fail_silently=True)
        return super(EditProfile, self).form_valid(form)


class Share(View):
    """
    Share via Facebook or Twitter.
    """
    type = None
    
    def get(self, request, *args, **kwargs):
        try:
            current_url = request.META['HTTP_REFERER']
            
            if self.type == 'Facebook':
                url = 'http://www.facebook.com/sharer/sharer.php?u=%s' % urllib.quote(current_url)
            elif self.type == 'Twitter':
                url = 'https://twitter.com/intent/tweet?original_referer=%s' % urllib.quote(current_url)
            else:
                return Http404()
            
            UserActivity.track_activity(user=request.user,
                                        activity=activity_constants.ACTIVITY_SOCIAL_SHARE,
                                        sub=ugettext('<a href="%s">%s</a> via %s' % (request.META['HTTP_REFERER'],
                                                                                     request.META['HTTP_REFERER'],
                                                                                     self.type)))
            
            return HttpResponseRedirect(url)
        except:
            return Http404()

def like(request, content_type, id, vote):
    #content_type = content_type.replace("-", ".")
    app, modelname = content_type.split('-')
    object = ContentType.objects.get(app_label=app, model__iexact=modelname).model_class().objects.get(id=id)

    if can_vote(object, request.user, request):
        UserActivity.track_activity(user=request.user.member,
                                    activity=activity_constants.ACTIVITY_LIKED,
                                    sub=ugettext('<a href="%s">%s</a>' % (object.get_absolute_url(),
                                                                          object.comment if isinstance(object, FoundryComment) else object.title)),
                                    content_object=object,
                                    image_object=object)
    return likes_views.like(request, content_type, id, vote)


# Caching duration matches the refresh rate
@cache_page(30) 
def fetch_new_comments_ajax(request, content_type_id, oid, last_comment_id):
    # xxx: not happy with this function. The idea was to re-use comment fetch 
    # logic but it feels slow.
    # Re-use template tag to fetch results
    context = RequestContext(request)
    context['object'] = ContentType.objects.get(
        id=content_type_id
    ).get_object_for_this_type(id=oid)
    t = Template("{% load comments %} {% get_comment_list for object as comment_list %}")
    t.render(context)

    # Trivial case
    if not context['comment_list']:
        return HttpResponse('')

    # Restrict object list to only newer comments
    # Stupid stupid django comments makes comment_list a list, so I can't 
    # filter it through the API.
    #context['comment_list'] = context['comment_list'].filter(id__gt=int(last_comment_id))
    li = []
    for o in context['comment_list']:
        if o.id > int(last_comment_id):
            li.append(o)
    context['comment_list'] = li

    return render_to_response('comments/list_new_comments.html', {}, context_instance=context)

@requires_csrf_token
def server_error(request, template_name='500.html'):
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request)))


@text_widget
def latest_5_new_members(request):
    members = Member.objects.all().order_by('-date_joined')[0:5]
    return [(member.username, TEXT_NONE) for member in members]

@text_widget
def top_5_user_agents(request):
    user_agents = UserAgent.objects.all().order_by('-hits')[0:5]
    return [(user_agent.user_agent, TEXT_NONE) for user_agent in user_agents]


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

