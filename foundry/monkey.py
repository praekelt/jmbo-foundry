"""We want to default to the last page when displaying comments.
django-autopaginate does not allow us to do this so a monkey-patch is
required."""

from django.core.paginator import Paginator, InvalidPage

from pagination.templatetags.pagination_tags import AutoPaginateNode

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
from django.contrib.comments.templatetags.comments import CommentListNode

def get_query_set(self, context):
    qs = super(CommentListNode, self).get_query_set(context)
    if context['request'].REQUEST.get('my_messages'):
        user = context['request'].user
        if user.is_authenticated():
            #qs = qs.filter()
            q1 = Q(user=user)
            q2 = Q(in_reply_to__user=user)
            qs = qs.filter(q1 | q2)
    return qs

CommentListNode.get_query_set = get_query_set
