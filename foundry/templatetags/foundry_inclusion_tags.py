from BeautifulSoup import BeautifulSoup

from django import template
from django.core.urlresolvers import reverse, resolve, NoReverseMatch
from django.template.loader import render_to_string
from django.conf import settings

from preferences import preferences

from foundry.models import Menu, Navbar, Listing
from foundry.templatetags import listing_styles

register = template.Library()


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
            obj = Menu.objects.get(slug=slug)
        except Menu.DoesNotExist:
            return ''

        object_list = []
        for o in obj.menulinkposition_set.all().order_by('position'):
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
            obj = Navbar.objects.get(slug=slug)
        except Navbar.DoesNotExist:
            return ''

        extra = {'object':obj}

        object_list = []
        active_link = None
        for o in obj.navbarlinkposition_set.all().order_by('position'):
            link = o.link
            object_list.append(link)
            if not active_link and link.is_active(context['request']):
                active_link = link

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
            obj = Listing.objects.get(slug=slug)
        except Listing.DoesNotExist:
            return ''

        return getattr(listing_styles, obj.style)(obj).render(context)


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

            # Call the view. Let any error propagate.
            html = view(context['request'], *args, **kwargs).content

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
