'''
Created on 08 Jul 2012

@author: euan
'''
from analytics.basemetric import BaseMetric
from foundry import models

class MemberRegistered(BaseMetric):
    uid   = "membersregistered"
    title = "members registered"

    def calculate(self, start_datetime, end_datetime):
        return models.Member.objects.filter(date_joined__gte=start_datetime,
            date_joined__lt=end_datetime).count()
    
    def get_earliest_timestamp(self):
        try:
            return models.Member.objects.all().order_by('date_joined')[0].date_joined
        except IndexError:
            return None
        
class PageImpressions(BaseMetric):
    uid   = "pageimpressions"
    title = "Page impressions"

    def calculate(self, start_datetime, end_datetime):
        return models.PageImpression.objects.filter(timestamp__gte=start_datetime,
                                                    timestamp__lt=end_datetime).count()
    
    def get_earliest_timestamp(self):
        try:
            return models.PageImpression.objects.all().order_by('timestamp')[0].timestamp
        except IndexError:
            return None
        
class BlogPosts(BaseMetric):
    uid   = "blogposts"
    title = "Blog posts"

    def calculate(self, start_datetime, end_datetime):
        return models.BlogPost.objects.filter(created__gte=start_datetime,
                                              created__lt=end_datetime).count()
    
    def get_earliest_timestamp(self):
        try:
            return models.BlogPost.objects.all().order_by('created')[0].created
        except IndexError:
            return None
        
class Comments(BaseMetric):
    uid   = "comments"
    title = "Comments"

    def calculate(self, start_datetime, end_datetime):
        return models.FoundryComment.objects.filter(submit_date__gte=start_datetime,
                                                    submit_date__lt=end_datetime).count()
    
    def get_earliest_timestamp(self):
        try:
            return models.FoundryComment.objects.all().order_by('submit_date')[0].submit_date
        except IndexError:
            return None
        
        