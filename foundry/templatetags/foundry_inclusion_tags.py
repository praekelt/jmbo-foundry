from BeautifulSoup import BeautifulSoup

from django import template
from django.core.urlresolvers import reverse, resolve, NoReverseMatch

from preferences import preferences

from foundry.templatetags import page_block_styles

register = template.Library()


@register.inclusion_tag('foundry/inclusion_tags/menu.html')
def menu():
    menu_preferences = preferences.MenuPreferences
    return {
        'object_list': menu_preferences.links.all().order_by(\
                'menulinkposition__position')
    }


@register.inclusion_tag('foundry/inclusion_tags/navbar.html', \
        takes_context=True)
def navbar(context):
    navbar_preferences = preferences.NavbarPreferences
    request = context['request']
    object_list = []
    active_link = None
    for link in navbar_preferences.links.all().order_by(\
            'navbarlinkposition__position'):
        object_list.append(link)
        if not active_link:
            if link.is_active(request):
                active_link = link

    return {
        'object_list': object_list,
        'active_link': active_link,
    }

@register.tag
def page_block(parser, token):
    try:
        tag_name, obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'page_block tag requires 1 argument (page_block), %s given' % \
                    (len(token.split_contents()) - 1)
            )
    return PageBlockNode(obj)

class PageBlockNode(template.Node):
    def __init__(self, obj):
        self.obj = template.Variable(obj)

    def render(self, context):
        obj = self.obj.resolve(context)
        return getattr(page_block_styles, obj.style)(obj).render(context)


@register.tag
def render_view(parser, token):
    try:
        tag_name, view_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'render_view tag requires argument view_name'
        )
    return RenderViewNode(view_name)


class RenderViewNode(template.Node):
    def __init__(self, view_name):
        self.view_name = template.Variable(view_name)

    def render(self, context):
        view_name = self.view_name.resolve(context)
        # Resolve view name to a function or object
        # xxx: this is slow because there is no way to get the view 
        # function / object directly from the view name - you have to pass 
        # through the url. But since the result is consistent while the 
        # Django process is running it is a good candidate for caching.
        try:
            url = reverse(view_name)        
        except NoReverseMatch:
            return "No reverse match for %s" % view_name
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


@register.tag
def view_url(parser, token):
    """Return the Url for a given view. Very similar to the {% url %} template tag, 
    but can accept a variable as first parameter."""
    try:
        tag_name, view_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'render_view tag requires argument view_name'
        )
    return ViewUrlNode(view_name)


class ViewUrlNode(template.Node):
    def __init__(self, view_name):
        self.view_name = template.Variable(view_name)

    def render(self, context):
        view_name = self.view_name.resolve(context)
        try:
            return reverse(view_name)        
        except NoReverseMatch:
            return ""
        view, args, kwargs = resolve(url)
