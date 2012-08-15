import types
from BeautifulSoup import BeautifulSoup

from django import template
from django.core.cache import cache
from django.core.urlresolvers import reverse, resolve, NoReverseMatch
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.conf import settings

from preferences import preferences

from foundry.models import Menu, Navbar, Listing, Page, Member
from foundry.templatetags import listing_styles

register = template.Library()


@register.filter(name='as_list')
def as_list(value, coerce=None):
    li = value.split()
    if coerce == 'int':
        li = [int(l) for l in li]
    return li


@register.filter(name='join_titles')
def join_titles(value, delimiter=', '):
    return delimiter.join([v.title for v in value])


@register.tag
def menu(parser, token):
    try:
        tag_name, slug = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'menu tag requires argument slug'
        )
    return MenuNode(slug)


class MenuNode(template.Node):

    def __init__(self, slug):
        self.slug = template.Variable(slug)

    def render(self, context, as_tile=False):       
        slug = self.slug.resolve(context)
        try:
            obj = Menu.permitted.get(slug=slug)
        except Menu.DoesNotExist:
            return ''

        object_list = []
        for o in obj.menulinkposition_set.all().order_by('position'):
            if o.condition_expression_result(context['request']):          
                # Glue name and class_name to o.link
                o.link.name = o.name
                o.link.class_name = o.class_name
                object_list.append(o.link)

        extra = {'object':obj, 'object_list':object_list}

        return render_to_string('foundry/inclusion_tags/menu.html', extra)


@register.tag
def navbar(parser, token):
    try:
        tag_name, slug = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'navbar tag requires argument slug'
        )
    return NavbarNode(slug)


class NavbarNode(template.Node):

    def __init__(self, slug):
        self.slug = template.Variable(slug)        

    def render(self, context, as_tile=False):
        slug = self.slug.resolve(context)
        try:
            obj = Navbar.permitted.get(slug=slug)
        except Navbar.DoesNotExist:
            return ''

        extra = {'object':obj}

        object_list = []
        active_link = None
        for o in obj.navbarlinkposition_set.all().order_by('position'):
            if o.condition_expression_result(context['request']):
                # Glue name and class_name to o.link
                o.link.name = o.name
                o.link.class_name = o.class_name
                object_list.append(o.link)
                if not active_link and o.link.is_active(context['request']):
                    active_link = o.link

        extra['object_list'] = object_list
        extra['active_link'] = active_link

        return render_to_string('foundry/inclusion_tags/navbar.html', extra)


@register.tag
def listing(parser, token):
    tokens = token.split_contents()
    length = len(tokens)
    
    if length < 2:
        raise template.TemplateSyntaxError(
            'listing tag require at least argument slug or queryset'
        )
   
    slug_or_queryset = tokens[1]

    kwargs = {}
    for token in tokens[2:]:
        k, v = token.split('=')
        kwargs[k] = v

    return ListingNode(slug_or_queryset, **kwargs)


class ListingNode(template.Node):

    def __init__(self, slug_or_queryset, **kwargs):
        self.slug_or_queryset = template.Variable(slug_or_queryset)
        self.kwargs = kwargs

    def render(self, context, as_tile=False):
        slug_or_queryset = self.slug_or_queryset.resolve(context)
        
        if isinstance(slug_or_queryset, types.UnicodeType):
            try:
                obj = Listing.permitted.get(slug=slug_or_queryset)
            except Listing.DoesNotExist:
                return ''

        else:
            class ListingProxy:
                """Helper class emulating Listing API so AbstractBaseStyle
                works. Essentially a record class."""

                def __init__(self, queryset, **kwargs):                    
                    self.queryset = lambda x: queryset
                    self.items_per_page = 0
                    for k, v in kwargs.items():
                        setattr(self, k, v)

            di = {}
            for k, v in self.kwargs.items():
                di[k] = template.Variable(v).resolve(context)
            obj = ListingProxy(slug_or_queryset, **di)

        return getattr(listing_styles, obj.style)(obj).render(context, as_tile=as_tile)


@register.tag
def rows(parser, token):
    try:
        tag_name, block_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'rows tag requires argument block_name'
        )
    return RowsNode(block_name)


class RowsNode(template.Node):
    def __init__(self, block_name):
        self.block_name = template.Variable(block_name)

    def render(self, context):
        # Recursion guard flag. Set by TileNode.
        if hasattr(context['request'], '_foundry_suppress_rows_tag'):
            return

        block_name = self.block_name.resolve(context)

        pages = Page.permitted.filter(is_homepage=True)
        if pages.count():
            page = pages[0]
            rows = page.rows_by_block_name.get(block_name, [])
            if rows:
                # We have customized rows for the block. Use them.
                return render_to_string(
                    'foundry/inclusion_tags/rows.html', {'rows':rows}, context
                )

        # Default rendering
        return render_to_string(
            'foundry/inclusion_tags/%s.html' % block_name, {}, context
        )


@register.tag
def tile(parser, token):
    try:
        tag_name, tile = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'tile tag requires argument tile'
        )
    return TileNode(tile)


class TileNode(template.Node):
    def __init__(self, tile):
        self.tile = template.Variable(tile)

    def render(self, context):
        tile = self.tile.resolve(context)

        # Evaluate condition
        if not tile.condition_expression_result(context['request']):
            return ''

        if tile.view_name:
            # Resolve view name to a function or object
            # xxx: this is slow because there is no way to get the view 
            # function / object directly from the view name - you have to pass 
            # through the url. But since the result is consistent while the 
            # Django process is running it is a good candidate for caching.     
            try:
                url = reverse(tile.view_name)        
            except NoReverseMatch:
                return "No reverse match for %s" % tile.view_name
            view, args, kwargs = resolve(url)

            # Set recursion guard flag
            setattr(context['request'], '_foundry_suppress_rows_tag', 1)            
            # Call the view. Let any error propagate.
            html = ''
            result = view(context['request'], *args, **kwargs)
            if isinstance(result, TemplateResponse):
                # The result of a generic view
                result.render()
                html = result.rendered_content
            elif isinstance(result, HttpResponse):
                # Old-school view
                html = result.content
            # Clear flag  
            # xxx: something may clear the flag. Need to investigate more 
            # incase of thread safety problem.
            if hasattr(context['request'], '_foundry_suppress_rows_tag'):           
                delattr(context['request'], '_foundry_suppress_rows_tag')

            # Extract content div. Currently there is no way to instruct a 
            # view to render only the content block, hence this.
            soup = BeautifulSoup(html)
            content = soup.find('div', id='content')        
            if content:
                return content.renderContents()

            # No content div found
            return html

        if tile.target:
            # Use convention to lookup node
            node = globals().get('%sNode' % tile.target.__class__.__name__)
            try:
                return node('"'+tile.target.slug+'"').render(context, as_tile=True)
            except:
                if settings.DEBUG:
                    raise
                return "A render error has occurred"


@register.tag
def tile_url(parser, token):
    """Return the Url for a given view. Very similar to the {% url %} template tag, 
    but can accept a variable as first parameter."""
    try:
        tag_name, tile = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'render_view tag requires argument tile'
        )
    return TileUrlNode(tile)


class TileUrlNode(template.Node):
    def __init__(self, tile):
        self.tile = template.Variable(tile)

    def render(self, context):
        tile = self.tile.resolve(context)
        if tile.view_name:
            try:
                return reverse(tile.view_name)        
            except NoReverseMatch:
                return ''

        if tile.target:
            # xxx: not strictly correct since target may be menu or navbar. 
            # No harm done for now.
            url = reverse('listing-detail', args=[tile.target.slug])
            return url

@register.tag
def get_listing_queryset(parser, token):
    """{% get_listing_queryset [slug] as [varname] %}"""
    try:
        tag_name, slug, dc, as_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "get_listing_queryset tag has syntax {% get_listing_items [slug] as [varname] %}"
        )
    return ListingQuerysetNode(slug, as_var)


class ListingQuerysetNode(template.Node):

    def __init__(self, slug, as_var):
        self.slug = template.Variable(slug)
        self.as_var = template.Variable(as_var)

    def render(self, context):
        slug = self.slug.resolve(context)
        as_var = self.as_var.resolve(context)
        try:
            obj = Listing.permitted.get(slug=slug)
            context[as_var] = obj.queryset(context['request'])
        except Listing.DoesNotExist:
            obj = None
            context[as_var] = None

        return ''
