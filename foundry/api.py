from django.conf.urls.defaults import url

from tastypie.resources import ModelResource
from tastypie import fields
from jmbo.api import ModelBaseResource, SlugResource

from foundry.models import Listing, Link, Navbar, Menu, Page, Row, Column, \
    Tile, BlogPost


class ListingResource(SlugResource):

    class Meta:
        queryset = Listing.permitted.all()
        resource_name = 'listing'
        allowed_methods = ['get']
        # only expose these fields
        fields = ('title', 'subtitle', 'slug', 'style')
    
    def get_list(self, request, **kwargs):
        self.get_type = 'list'
        return super(ListingResource, self).get_list(request, **kwargs)

    def get_detail(self, request, **kwargs):
        self.get_type = 'detail'
        return super(ListingResource, self).get_detail(request, **kwargs)

    def dehydrate(self, bundle):
        if self.get_type == 'detail':
            bundle.data['objects'] = []
            # Batching
            listing = bundle.obj
            qs = listing.queryset()
            if listing.count:
                qs[:listing.count]
            total_count = qs.count()
            bundle.data['meta'] = {'total_count': total_count}
            if listing.items_per_page:
                # The seemingly strange page calculation is due to
                # django-paginations's middleware.
                page = max(getattr(bundle.request, 'page', 1), 1)
                offset = (page-1) * listing.items_per_page
                qs = qs[offset:offset+listing.items_per_page]
                # calculate the uris for next and previous page
                qd = bundle.request.GET.copy()
                if 'page' in qd:
                    del qd['page']
                uri = "%s?%s" % (self.get_resource_uri(listing), qd.urlencode())
                bundle.data['meta']['next'] = None if offset + listing.items_per_page > total_count \
                    else "%s&page=%d" % (uri, page + 1)
                bundle.data['meta']['previous'] = None if page <= 1 else "%s&page=%d" % (uri, page - 1)

            as_leaf = (bundle.request.GET.get('as_leaf_class', '') == '1')
            mbr = ModelBaseResource(as_leaf=as_leaf)
            for obj in qs:
                if as_leaf:
                    b = mbr.full_dehydrate(mbr.build_bundle(obj.as_leaf_class(), request=bundle.request))
                else:
                    b = mbr.full_dehydrate(mbr.build_bundle(obj, request=bundle.request))
                bundle.data['objects'].append(b)

        return bundle


'''class LinkResource(ModelResource):

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
        return bundle'''
