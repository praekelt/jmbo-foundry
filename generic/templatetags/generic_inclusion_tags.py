from django import template

from preferences import preferences

register = template.Library()


@register.inclusion_tag('generic/inclusion_tags/menu.html')
def menu():
    menu_preferences = preferences.MenuPreferences
    return {
        'object_list': menu_preferences.links.all().order_by(\
                'menulinkposition__position')
    }


@register.inclusion_tag('generic/inclusion_tags/navbar.html', \
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
