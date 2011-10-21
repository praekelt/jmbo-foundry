from django import template

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
