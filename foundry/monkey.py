"""We want to default to the last page when displaying comments.
django-autopaginate does not allow us to do this so a monkey-patch is
required."""

from django.core.paginator import Paginator, InvalidPage
from django.conf import settings

from pagination.templatetags.pagination_tags import AutoPaginateNode

INVALID_PAGE_RAISES_404 = getattr(
    settings,'PAGINATION_INVALID_PAGE_RAISES_404', False
)


def render(self, context):
    key = self.queryset_var.var
    value = self.queryset_var.resolve(context)
    if isinstance(self.paginate_by, int):
        paginate_by = self.paginate_by
    else:
        paginate_by = self.paginate_by.resolve(context)
    paginator = Paginator(value, paginate_by, self.orphans)
    page = context['request'].page
    if page == -1:
        page = paginator.num_pages
    try:
        page_obj = paginator.page(page)
    except InvalidPage:
        if INVALID_PAGE_RAISES_404:
            raise Http404('Invalid page requested.  If DEBUG were set to ' +
                'False, an HTTP 404 page would have been shown instead.')
        context[key] = []
        context['invalid_page'] = True
        return u''
    if self.context_var is not None:
        context[self.context_var] = page_obj.object_list
    else:
        context[key] = page_obj.object_list
    context['paginator'] = paginator
    context['page_obj'] = page_obj
    return u''

AutoPaginateNode.render = render


"""CommentListNode must be able to return only comments related to the
authenticated user. Add a method to the class."""

from django.db.models import Q
from django.db.models.aggregates import Max
from django.contrib.comments.templatetags.comments import CommentListNode

def get_query_set(self, context):
    qs = super(CommentListNode, self).get_query_set(context)
    if context['request'].REQUEST.get('my_messages'):
        user = context['request'].user
        if user.is_authenticated():
            q1 = Q(user=user)
            q2 = Q(in_reply_to__user=user)
            qs = qs.filter(q1 | q2)

    # Inject last comment id in context. This is a convenient place.
    setattr(context, 'foundry_last_comment_id', qs.aggregate(Max('id'))['id__max'] or 0)

    return qs

CommentListNode.get_query_set = get_query_set


"""Django forms displays errors in a <ul> tag and provides no easy mechanism to
override this behaviour. Patch the __unicode__ method to use <div> tags."""

from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import ErrorList

def errorlist_as_div(self):
    if not self: return u''
    return mark_safe(
        u'<div class="errorlist">%s</div>' \
            % ''.join([u'<div class="error">%s</div>' % conditional_escape(force_unicode(e)) for e in self])
    )

ErrorList.__unicode__ = errorlist_as_div


"""Patch photologue so PhotoSizeCache is layer aware"""
import re

from django.utils.functional import curry
from django.conf import settings

import photologue
from photologue.models import PhotoSize, ImageModel

def add_accessor_methods(self, *args, **kwargs):
    for size in PhotoSizeCache().sizes.keys():
        setattr(self, 'get_%s_size' % size,
                curry(self._get_SIZE_size, size=size))
        setattr(self, 'get_%s_photosize' % size,
                curry(self._get_SIZE_photosize, size=size))
        setattr(self, 'get_%s_url' % size,
                curry(self._get_SIZE_url, size=size))
        setattr(self, 'get_%s_filename' % size,
                curry(self._get_SIZE_filename, size=size))

        layers = settings.FOUNDRY['layers']
        layer_size = re.sub(r'_(%s)$' % '|'.join(layers), '', size) + '_LAYER'
        setattr(self, 'get_%s_size' % layer_size,
                curry(self._get_SIZE_size, size=layer_size))
        setattr(self, 'get_%s_photosize' % layer_size,
                curry(self._get_SIZE_photosize, size=layer_size))
        setattr(self, 'get_%s_url' % layer_size,
                curry(self._get_SIZE_url, size=layer_size))
        setattr(self, 'get_%s_filename' % layer_size,
                curry(self._get_SIZE_filename, size=layer_size))

ImageModel.add_accessor_methods = add_accessor_methods


class LayerAwareSizes(dict):
    
    def get(self, key):
        result = None

        # Handle legacy LAYER marker
        if key.endswith('_LAYER'):
            key = key.replace('_LAYER', '') 

        # Iterate over layers
        for layer in settings.FOUNDRY['layers']:
            result = super(LayerAwareSizes, self).get(key + '_' + layer)
            if result is not None:
                break

        # Fall back to default
        if result is None:
            result = super(LayerAwareSizes, self).get(key)

        return result


class PhotoSizeCache(object):
    __state = {"sizes": LayerAwareSizes()}

    def __init__(self):
        self.__dict__ = self.__state
        if not len(self.sizes):
            sizes = PhotoSize.objects.all()
            for size in sizes:
                self.sizes[size.name] = size

    def reset(self):
        self.sizes = LayerAwareSizes()

photologue.models.PhotoSizeCache = PhotoSizeCache


"""Patch {% block %} so we can inject side columns."""
from django.template.loader_tags import BlockNode, BLOCK_CONTEXT_KEY
from django.core.urlresolvers import resolve, Resolver404
from django.template.loader import render_to_string

def BlockNode_render(self, context):
    block_context = context.render_context.get(BLOCK_CONTEXT_KEY)
    context.push()
    if block_context is None:
        context['block'] = self
        result = self.nodelist.render(context)
    else:
        push = block = block_context.pop(self.name)
        if block is None:
            block = self
        # Create new block so we can store context without thread-safety issues.
        block = BlockNode(block.name, block.nodelist)
        block.context = context
        context['block'] = block
        result = block.nodelist.render(context)
        if push is not None:
            block_context.push(self.name, push)
    context.pop()

    if (self.name == 'content') and not hasattr(context['request'], '_foundry_blocknode_marker'):
        # What view are we rendering?
        try:
            view_name = resolve(context['request'].META['PATH_INFO']).view_name
        except Resolver404:
            return result

        # Mark to prevent recursion
        setattr(context['request'], '_foundry_blocknode_marker', 1)

        # Find page if any. Import here to prevent circular import.
        from foundry.models import Page, PageView
        # Use first permitted page that has row of required type
        pages = Page.permitted.filter(id__in=[o.page.id for o in PageView.objects.filter(view_name=view_name)])
        for page in pages:
            rows = page.row_set.filter(has_left_or_right_column=True)
            if rows.exists():
                html = render_to_string(
                    'foundry/inclusion_tags/rows.html', {'rows':[rows[0]], 'include_center_marker':1}, context
                )
                return html.replace('_FOUNDRY_BLOCKNODE_PLACEHOLDER', result)

    return result

#BlockNode.render = BlockNode_render


"""Django wraps the already hidden CSRF token input in an invisible container. This causes problems on low-end handsets. 
https://code.djangoproject.com/ticket/18484"""
from django.template.defaulttags import CsrfTokenNode
from django.utils.safestring import mark_safe
from django.conf import settings

def CsrfTokenNode_render(self, context):
    csrf_token = context.get('csrf_token', None)
    if csrf_token:
        if csrf_token == 'NOTPROVIDED':
            return mark_safe(u"")
        else:
            return mark_safe(u"<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % csrf_token)
    else:
        # It's very probable that the token is missing because of
        # misconfiguration, so we raise a warning
        from django.conf import settings
        if settings.DEBUG:
            import warnings
            warnings.warn("A {% csrf_token %} was used in a template, but the context did not provide the value.  This is usually caused by not using RequestContext.")
        return u''

CsrfTokenNode.render = CsrfTokenNode_render


"""Patch django.contrib.sites.models.Site.__unicode__ so it returns name and
not domain. The UI gets confusing since we have up to three sites comprising
one logical mobi site."""
from django.contrib.sites.models import Site

def Site__unicode__(self):
    return self.name

def Site_title(self):
    # Strip away (smart), (web) etc
    return self.name.split('(')[0]

Site.__unicode__ = Site__unicode__    
Site.title = Site_title
