"""Patch BaseCommentNode queryset method so comments are not constrained to
only one site. Our convention is that basic, smart and web site ids always fall
into a certain numerical range.  Use this fact to relax the query."""

from django.contrib.comments.templatetags.comments import BaseCommentNode
from django.utils.encoding import smart_unicode
from django.conf import settings

def BaseCommentNode_get_query_set(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return self.comment_model.objects.none()

        # Compute site id range
        i = settings.SITE_ID / 10
        site_ids = range(i * 10 + 1, (i + 1) * 10)

        qs = self.comment_model.objects.filter(
            content_type = ctype,
            object_pk    = smart_unicode(object_pk),
            site__pk__in = site_ids,
        )

        # The is_public and is_removed fields are implementation details of the
        # built-in comment model's spam filtering system, so they might not
        # be present on a custom comment model subclass. If they exist, we
        # should filter on them.
        field_names = [f.name for f in self.comment_model._meta.fields]
        if 'is_public' in field_names:
            qs = qs.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True) and 'is_removed' in field_names:
            qs = qs.filter(is_removed=False)

        return qs

BaseCommentNode.get_query_set = BaseCommentNode_get_query_set


"""CommentListNode must be able to return only comments related to the
authenticated user. Add a method to the class."""

from django.db.models import Q
from django.db.models.aggregates import Max
from django.contrib.comments.templatetags.comments import CommentListNode

def CommentListNode_get_query_set(self, context):
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

CommentListNode.get_query_set = CommentListNode_get_query_set


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
        layer_size = re.sub(r'_(%s)$' % '|'.join(layers), '', size)
        setattr(self, 'get_%s_size' % layer_size,
                curry(self._get_SIZE_size, size=layer_size))
        setattr(self, 'get_%s_photosize' % layer_size,
                curry(self._get_SIZE_photosize, size=layer_size))
        setattr(self, 'get_%s_url' % layer_size,
                curry(self._get_SIZE_url, size=layer_size))
        setattr(self, 'get_%s_filename' % layer_size,
                curry(self._get_SIZE_filename, size=layer_size))

        # The _LAYER marker is legacy that needs to be maintained.
        setattr(self, 'get_%s_LAYER_size' % layer_size,
                curry(self._get_SIZE_size, size=layer_size))
        setattr(self, 'get_%s_LAYER_photosize' % layer_size,
                curry(self._get_SIZE_photosize, size=layer_size))
        setattr(self, 'get_%s_LAYER_url' % layer_size,
                curry(self._get_SIZE_url, size=layer_size))
        setattr(self, 'get_%s_LAYER_filename' % layer_size,
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


"""Legacy templates do {% autopaginate object_list items_per_page %} because it
was guaranteed to be non-zero. That led to an inefficiency which was removed.
This patch ensures legacy templates do not break."""
from pagination.templatetags import pagination_tags
def AutoPaginateNode_decorator(func):
    def new(self, context):
        if isinstance(self.paginate_by, int):
            paginate_by = self.paginate_by
        else:
            paginate_by = self.paginate_by.resolve(context)
        if not paginate_by:
            self.paginate_by = 100
        return func(self, context)
    return new

pagination_tags.AutoPaginateNode.render = AutoPaginateNode_decorator(pagination_tags.AutoPaginateNode.render)
