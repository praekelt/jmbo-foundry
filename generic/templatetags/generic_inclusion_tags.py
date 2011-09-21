from django import template

from preferences import preferences

register = template.Library()


@register.inclusion_tag('generic/inclusion_tags/footer_menu.html')
def footer_menu():
    footer_menu_preferences = preferences.FooterMenuPreferences
    return {
        'object_list': footer_menu_preferences.links.all()
    }
