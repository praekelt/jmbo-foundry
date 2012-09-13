import random
import urllib

from django.conf import settings
from django.contrib.auth import authenticate, login, get_backends
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, \
    HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required
from django.db.models import Q, get_model
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.models import get_current_site
from django.template import Template
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import requires_csrf_token
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.db.models import Q
from django.utils import timezone
from django.template.loader import get_template_from_string
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.utils.html import strip_tags

# Comment post required imports
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.views.decorators.http import require_POST
from django.utils import simplejson
from django.utils.html import escape
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib import comments
from django.contrib.comments import signals
from django.http import QueryDict
from django.contrib.comments.views.utils import next_redirect
from django.contrib.comments.views.comments import comment_done

from category.models import Category
from jmbo.models import ModelBase
from jmbo.generic.views import GenericObjectDetail, GenericObjectList
from jmbo.view_modifiers import DefaultViewModifier
from preferences import preferences

from foundry.models import Listing, Page, ChatRoom, BlogPost, Notification, \
    Member, FoundryComment, CommentReport
from foundry.forms import JoinForm, JoinFinishForm, AgeGatewayForm, TestForm, \
    SearchForm, CreateBlogPostForm


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
            param = urllib.quote(form.cleaned_data['search_term'])
            return HttpResponseRedirect(
                reverse('search-results') + '?search_term=' + param
            )
    else:
        form = SearchForm() 

    extra = dict(form=form)
    return render_to_response('foundry/search.html', extra, context_instance=RequestContext(request))


def search_results(request):
    search_term = request.REQUEST.get('search_term', '')
    if search_term:
        q1 = Q(title__icontains=search_term)
        q2 = Q(description__icontains=search_term)
        queryset = ModelBase.permitted.filter(q1|q2)
    else:
        queryset = ModelBase.objects.none()
    extra = dict(
        items_per_page=10,
        search_term=search_term, 
        queryset=queryset
    )
    return render_to_response('foundry/search_results.html', extra, context_instance=RequestContext(request))


@require_POST
def post_comment(request, next=None, using=None):
    """
    Adapted from django.contrib.comments. Preview functionality removed and 
    made ajax aware.
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email

    # Check to see if the POST data overrides the view's next argument.
    next = data.get("next", next)

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = get_model(*ctype.split(".", 1))
        target = model._default_manager.using(using).get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError), e:
        return CommentPostBadRequest(
            "Attempting go get content-type %r and object PK %r exists raised %s" % \
                (escape(ctype), escape(object_pk), e.__class__.__name__))

    # Construct the comment form
    form = comments.get_form()(target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))

    # If there are errors show the comment
    if form.errors:
        # Pass a list of templates
        app_label, model = ctype.split('.')
        template_name = [
            "comments/%s/%s/form.html" % (app_label, model),
            "comments/%s/form.html" % app_label,
            "comments/form.html"
        ]
        return render_to_response(
            template_name,
            {
                "comment" : form.data.get("comment", ""),
                "form" : form,
                "next": next,
            },
            RequestContext(request, {})
        )

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    if not request.is_ajax():
        return next_redirect(data, next, comment_done, c=comment._get_pk_val())
    else:
        # Return rendered comment list
        context = RequestContext(request)
        # Put paginate by as a GET variable so django-pagination works
        context['request'].GET = QueryDict('paginate_by=%s' % request.POST['paginate_by'])
        context['object'] = target
        t = Template("{% load comments %} {% render_comment_list for object %}")
        html = t.render(context)
        di = {'status': 'success', 'html': html, 'obj_id': comment.id}
        return HttpResponse(simplejson.dumps(di))
        

def comment_reply_form(request):
    # This view is used when the browser has no javascript support
    obj = ContentType.objects.get(
        id=request.GET['content_type_id']
    ).get_object_for_this_type(id=request.GET['oid'])
    extra = {'object': obj, 'next': request.GET['next']}
    return render_to_response('foundry/comment_reply_form.html', extra, context_instance=RequestContext(request))


@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(FoundryComment, id=comment_id)

    # Only create object if user is allowed to report
    if comment.can_report(request):
        CommentReport.objects.create(comment=comment, reporter=request.user)

        # Send mail when 3 reports are reached. Re-use naughty word template.
        if comment.commentreport_set.count() == 3:
            from foundry.management.commands.report_naughty_words import TEMPLATE
            site = get_current_site(request)
            template = get_template_from_string(TEMPLATE)
            c = dict(comments=[comment], site_domain=site.domain)
            content = template.render(Context(c))
            msg = EmailMultiAlternatives(
                "Flagged comment on %s" % site.name, 
                strip_tags(content), 
                settings.DEFAULT_FROM_EMAIL, 
                preferences.NaughtyWordPreferences.email_recipients.split()
            )
            msg.attach_alternative(content, 'text/html')
            msg.send()

    next = request.REQUEST.get('next')
    response = HttpResponseRedirect(next or comment.content_object.get_absolute_url())
    # Set cookie since it is very expensive to query whether a user may report
    # a comment for each comment.
    response.set_cookie(
        'comment_report_%s' % comment.id,
        value=1, 
        max_age=7*86400
    )
    return response


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
            msg = _("The blog post %s has been saved") % instance.title
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect('/')
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


@receiver(user_logged_in)
def set_session_expiry(sender, request, user, **kwargs):
    # Override session expiry date. We effectively ignore
    # SESSION_EXPIRE_AT_BROWSER_CLOSE.
    if request.REQUEST.get('remember_me'):
        now = timezone.now()
        expires = now.replace(year=now.year+10)
        request.session.set_expiry(expires)
    else:
        request.session.set_expiry(0)
