from BeautifulSoup import BeautifulSoup

from django import template
from django.core.urlresolvers import reverse, resolve, NoReverseMatch
from django.template.loader import render_to_string
from django.conf import settings

from preferences import preferences

from foundry.models import Menu, Navbar, Listing, Page, Relation
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

    def render(self, context):       
        slug = self.slug.resolve(context)
        try:
            obj = Menu.permitted.get(slug=slug)
        except Menu.DoesNotExist:
            return ''

        object_list = []
        for o in obj.menulinkposition_set.all().order_by('position'):
            if o.condition_expression_result(context['request']):          
                # Glue class_name to o.link
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

    def render(self, context):
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
                # Glue class_name to o.link
                o.link.class_name = o.class_name
                object_list.append(o.link)
                if not active_link and o.link.is_active(context['request']):
                    active_link = o.link

        extra['object_list'] = object_list
        extra['active_link'] = active_link

        return render_to_string('foundry/inclusion_tags/navbar.html', extra)


@register.tag
def listing(parser, token):
    try:
        tag_name, slug = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'listing tag requires argument slug'
        )
    return ListingNode(slug)


class ListingNode(template.Node):

    def __init__(self, slug):
        self.slug = template.Variable(slug)

    def render(self, context):
        slug = self.slug.resolve(context)
        try:
            obj = Listing.permitted.get(slug=slug)
        except Listing.DoesNotExist:
            return ''

        return getattr(listing_styles, obj.style)(obj).render(context)


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
            html = view(context['request'], *args, **kwargs).content
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
                return node('"'+tile.target.slug+'"').render(context)
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
def get_relation_list(parser, token):
    """Gets list of relations from object identified by a relation name.

    Syntax::

        {% get_relation_list [relation_name] for [object] as [varname] %}
    """
    tokens = token.contents.split()
    if len(tokens) != 6:
        raise template.TemplateSyntaxError("%r tag requires 6 arguments" % tokens[0])

    if tokens[2] != 'for':
        raise template.TemplateSyntaxError("Third argument in %r tag must be 'for'" % tokens[0])

    if tokens[4] != 'as':
        raise template.TemplateSyntaxError("Fifth argument in %r tag must be 'as'" % tokens[0])

    return RelationListNode(name=tokens[1], obj=tokens[3], as_var=tokens[5])

      

class RelationListNode(template.Node):

    def __init__(self, name, obj, as_var):
        self.name = template.Variable(name)
        self.obj = template.Variable(obj)
        self.as_var = template.Variable(as_var)

    def render(self, context):
        name = self.name.resolve(context)
        obj = self.obj.resolve(context)
        as_var = self.as_var.resolve(context)

        relations = Relation.objects.filter(
            source_content_type=obj.content_type, 
            source_object_id=obj.id,
            name=name
        )
        # Unpack. Relation set is small by nature.
        context[as_var] = [o.target for o in relations if o.target.is_permitted]

        return ''
