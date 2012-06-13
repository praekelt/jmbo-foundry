from tastypie.resources import ModelResource
from tastypie import fields
from jmbo.api import ModelBaseResource

from foundry.models import Listing, BlogPost


class ListingResource(ModelResource):

    class Meta:
        queryset = Listing.permitted.all()
        resource_name = 'listing'

    def dehydrate(self, bundle):
        bundle.data['permalink'] = bundle.obj.get_absolute_url()
        bundle.data['items'] = []
        for o in bundle.obj.queryset:
            mbr = ModelBaseResource()
            b = mbr.full_dehydrate(mbr.build_bundle(o))
            bundle.data['items'].append(b)
        return bundle

    
class BlogPostResource(ModelResource):

    class Meta:
        queryset = BlogPost.permitted.all()
        resource_name = 'blogpost'
