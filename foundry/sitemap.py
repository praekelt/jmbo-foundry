from django.contrib.sites.models import get_current_site
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps import Sitemap, FlatPageSitemap

from foundry.models import Navbar, Menu


"""Slight adaptation of default Django sitemaps view passes request to callable
site object"""
@cache_page(60*5)
def sitemap(request, sitemaps, section=None,
            template_name='sitemap.xml', mimetype='application/xml'):
    req_protocol = 'https' if request.is_secure() else 'http'
    req_site = get_current_site(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps = [sitemaps[section]]
    else:
        maps = sitemaps.values()
    page = request.GET.get("p", 1)

    urls = []
    for site in maps:
        try:
            if callable(site):
                try:
                    site = site(request)
                except TypeError:
                    site = site()
            urls.extend(site.get_urls(page=page, site=req_site,
                                      protocol=req_protocol))
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)
    return TemplateResponse(request, template_name, {'urlset': urls},
                            content_type=mimetype)


class BaseLinkSitemap(Sitemap):

    def __init__(self, request):
        self.request = request
        super(BaseLinkSitemap, self).__init__()

    def get_containers(self):
        raise NotImplementedError

    def items(self):
        added = []
        links = []
        linkposition_set = None
        for obj in self.get_containers():
            if linkposition_set is None:
                linkposition_set = getattr(obj, obj.__class__.__name__.lower() \
                    + 'linkposition_set')
            for o in linkposition_set.select_related().all().order_by('position'):
                if o.condition_expression_result(self.request) \
                    and (o.link.id not in added):
                    links.append(o.link)
                    added.append(o.link.id)
        return links


class MainNavbarLinkSitemap(BaseLinkSitemap):
    priority = 1.0

    def get_containers(self):
        return Navbar.permitted.filter(slug='main')


class MainMenuLinkSitemap(BaseLinkSitemap):
    priority = 1.0

    def get_containers(self):
        return Menu.permitted.filter(slug='main')


class SubNavbarsLinkSitemap(BaseLinkSitemap):
    priority = 0.75

    def get_containers(self):
        return Navbar.permitted.all().exclude(slug='main')


class SubMenusLinkSitemap(BaseLinkSitemap):
    priority = 0.75

    def get_containers(self):
        return Menu.permitted.all().exclude(slug='main')


sitemaps = {
    'flatpages': FlatPageSitemap,
    'main-navbar': MainNavbarLinkSitemap,
    'main-menu': MainMenuLinkSitemap,
    'sub-navbars': SubNavbarsLinkSitemap,
    'sub-menus': SubMenusLinkSitemap,
}
