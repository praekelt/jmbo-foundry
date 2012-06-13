from tastypie.resources import ModelResource
from tastypie import fields
from jmbo.api import ModelBaseResource

from foundry.models import Listing, Link, Navbar, Menu, BlogPost


class ListingResource(ModelResource):

    class Meta:
        queryset = Listing.permitted.all()
        resource_name = 'listing'

    def dehydrate(self, bundle):
        bundle.data['permalink'] = bundle.obj.get_absolute_url()
        bundle.data['items'] = []
        for o in bundle.obj.queryset:
            r = ModelBaseResource()
            b = r.full_dehydrate(r.build_bundle(o))
            bundle.data['items'].append(b)
        return bundle


class LinkResource(ModelResource):

    class Meta:
        queryset = Link.objects.all()
        resource_name = 'link'


class NavbarResource(ModelResource):

    class Meta:
        queryset = Navbar.permitted.all()
        resource_name = 'navbar'

    def dehydrate(self, bundle):
        bundle.data['items'] = []
        for o in bundle.obj.navbarlinkposition_set.all().order_by('position'):
            if o.condition_expression_result(bundle.request):
                # Glue name and class_name to o.link
                o.link.name = o.name
                o.link.class_name = o.class_name
                r = LinkResource()
                b = r.full_dehydrate(r.build_bundle(o.link))
                bundle.data['items'].append(b)
        return bundle

   
class BlogPostResource(ModelResource):

    class Meta:
        queryset = BlogPost.permitted.all()
        resource_name = 'blogpost'
