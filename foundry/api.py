from django.conf.urls.defaults import url

from tastypie.resources import ModelResource
from tastypie import fields
from jmbo.api import ModelBaseResource

from foundry.models import Listing, Link, Navbar, Menu, Page, Row, Column, \
    Tile, BlogPost


class ListingResource(ModelResource):

    class Meta:
        queryset = Listing.permitted.all()
        resource_name = 'listing'

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def dehydrate(self, bundle):        
        bundle.data['resource_name'] = self._meta.resource_name
        bundle.data['permalink'] = bundle.obj.get_absolute_url()
        bundle.data['items'] = []

        # Batching
        link = bundle.obj
        qs = link.queryset()
        if link.items_per_page:
            # The seemingly strange page calculation is due to
            # django-paginations's middleware.
            page = max(getattr(bundle.request, 'page', 1), 1)
            offset = (page-1) * link.items_per_page
            qs = qs[offset:offset+link.items_per_page]

        for o in qs:
            r = ModelBaseResource()
            b = r.full_dehydrate(r.build_bundle(o, request=bundle.request))
            bundle.data['items'].append(b)
        return bundle


class LinkResource(ModelResource):

    class Meta:
        queryset = Link.objects.all()
        resource_name = 'link'
        fields = ('title',)

    def dehydrate(self, bundle):
        bundle.data['resource_name'] = self._meta.resource_name
        bundle.data['permalink'] = bundle.obj.get_absolute_url()
        return bundle


class NavbarResource(ModelResource):

    class Meta:
        queryset = Navbar.permitted.all()
        resource_name = 'navbar'

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def dehydrate(self, bundle):
        bundle.data['resource_name'] = self._meta.resource_name
        bundle.data['items'] = []
        for o in bundle.obj.navbarlinkposition_set.all().order_by('position'):
            if o.condition_expression_result(bundle.request):
                # Glue name and class_name to o.link
                o.link.name = o.name
                o.link.class_name = o.class_name
                r = LinkResource()
                b = r.full_dehydrate(r.build_bundle(o.link, request=bundle.request))
                bundle.data['items'].append(b)
        return bundle

 
class MenuResource(ModelResource):

    class Meta:
        queryset = Menu.permitted.all()
        resource_name = 'menu'

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def dehydrate(self, bundle):
        bundle.data['resource_name'] = self._meta.resource_name
        bundle.data['items'] = []
        for o in bundle.obj.menulinkposition_set.all().order_by('position'):
            if o.condition_expression_result(bundle.request):
                # Glue name and class_name to o.link
                o.link.name = o.name
                o.link.class_name = o.class_name
                r = LinkResource()
                b = r.full_dehydrate(r.build_bundle(o.link, request=bundle.request))
                bundle.data['items'].append(b)
        return bundle
  

class TileResource(ModelResource):

    class Meta:
        queryset = Tile.objects.all()
        resource_name = 'tile'

    def dehydrate(self, bundle):
        bundle.data['resource_name'] = self._meta.resource_name
        bundle.data['content'] = ''

        tile = bundle.obj

        # Evaluate condition
        if not tile.condition_expression_result(bundle.request):
            return bundle

        if tile.view_name:
            # No implemented yet
            return bundle

        if tile.target:
            # Use convention to lookup resource
            r = globals().get('%sResource' % tile.target.__class__.__name__)()
            b = r.full_dehydrate(r.build_bundle(tile.target, request=bundle.request))
            bundle.data['content'] = b

        return bundle


class ColumnResource(ModelResource):

    class Meta:
        queryset = Column.objects.all()
        resource_name = 'column'

    def dehydrate(self, bundle):
        bundle.data['resource_name'] = self._meta.resource_name
        tiles = []
        for tile_obj in bundle.obj.tiles:
            r = TileResource()
            b = r.full_dehydrate(r.build_bundle(tile_obj, request=bundle.request))
            tiles.append(b)
        bundle.data['tiles'] = tiles
        return bundle


class RowResource(ModelResource):

    class Meta:
        queryset = Row.objects.all()
        resource_name = 'row'

    def dehydrate(self, bundle):
        bundle.data['resource_name'] = self._meta.resource_name
        columns = []
        for column_obj in bundle.obj.columns:
            r = ColumnResource()
            b = r.full_dehydrate(r.build_bundle(column_obj, request=bundle.request))
            columns.append(b)
        bundle.data['columns'] = columns
        return bundle


class PageResource(ModelResource):

    class Meta:
        queryset = Page.permitted.all()
        resource_name = 'page'

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def dehydrate(self, bundle):
        bundle.data['resource_name'] = self._meta.resource_name
        rows = []
        for row_obj in bundle.obj.rows_by_block_name['content']:
            r = RowResource()
            b = r.full_dehydrate(r.build_bundle(row_obj, request=bundle.request))
            rows.append(b)
        bundle.data['rows'] = rows
        return bundle

class BlogPostResource(ModelResource):

    class Meta:
        queryset = BlogPost.permitted.all()
        resource_name = 'blogpost'

    def dehydrate(self, bundle):
        bundle.data['resource_name'] = self._meta.resource_name
        return bundle
