import inspect

from django.template.loader import render_to_string
from django.utils.importlib import import_module
from django.conf import settings


class AbstractBaseStyle(object):

    def __init__(self, listing):
        self.listing = listing

    def get_queryset(self, request=None):
        return self.listing.queryset(request)

    def get_pinned_queryset(self):
        # Check for pinned_queryset. It can be missing since listings can be
        # called via the {% listing %} tag. The resulting proxy listing object
        # does not neccessarily have the property.
        from jmbo.models import ModelBase
        return getattr(self.listing, 'pinned_queryset', ModelBase.objects.none())

    def get_context_data(self, context, as_tile=False):
        request = context['request']

        context['object_list'] = self.get_queryset(request)
        context['pinned_list'] = self.get_pinned_queryset()
        context['listing'] = self.listing
        context['items_per_page'] = self.listing.items_per_page
        context['identifier'] = getattr(self.listing, 'id', None) \
            or getattr(self.listing, 'identifier', '')

        context['view_modifier'] = None
        view_modifier = getattr(self.listing, 'view_modifier', None)
        if view_modifier:
            mod, attr = view_modifier.rsplit('.', 1)
            context['view_modifier'] = getattr(import_module(mod), attr)(request)

        context['display_title'] = True
        if as_tile and not self.listing.display_title_tiled:
            context['display_title'] = False

        return context

    def render(self, context, as_tile=False):
        context.push()
        result = render_to_string(self.template_name, self.get_context_data(context, as_tile=as_tile))
        context.pop()
        return result


class Horizontal(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_horizontal.html'
    image_path = "/admin/images/listing-horizontal.png"


class Vertical(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_vertical.html'
    image_path = "/admin/images/listing-vertical.png"


class Promo(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_promo.html'
    image_path = "/admin/images/listing-promo.png"


class VerticalThumbnail(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_vertical_thumbnail.html'
    image_path = "/admin/images/listing-vertical-thumbnail.png"


class Widget(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_widget.html'
    image_path = "/admin/images/listing-widget.png"


class CustomOne(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_custom_one.html'
    image_path = "/admin/images/listing-custom-one.png"


class CustomTwo(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_custom_two.html'
    image_path = "/admin/images/listing-custom-two.png"


class CustomThree(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_custom_three.html'
    image_path = "/admin/images/listing-custom-three.png"


class CustomFour(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_custom_four.html'
    image_path = "/admin/images/listing-custom-four.png"


class CustomFive(AbstractBaseStyle):
    template_name = 'foundry/inclusion_tags/listing_custom_five.html'
    image_path = "/admin/images/listing-custom-five.png"


LISTING_CLASSES = []
LISTING_MAP = {}
for klass in (Horizontal, Vertical, Promo, VerticalThumbnail, Widget):
    LISTING_CLASSES.append(klass)
    LISTING_MAP[klass.__name__] = klass
for app in settings.INSTALLED_APPS:
    if app == 'foundry':
        continue
    try:
        mod = import_module(app + '.templatetags.listing_styles')
    except ImportError:
        pass
    else:
        for name, klass in inspect.getmembers(mod, inspect.isclass):
            if name != 'AbstractBaseStyle':
                LISTING_CLASSES.append(klass)
                LISTING_MAP[klass.__name__] = klass
for klass in (CustomOne, CustomTwo, CustomThree, CustomFour, CustomFive):
    LISTING_CLASSES.append(klass)
    LISTING_MAP[klass.__name__] = klass
