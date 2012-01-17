from django.db import models
from django.conf import settings


class PermittedManager(models.Manager):

    def get_query_set(self):
        # Filter objects for current site
        return super(PermittedManager, self).get_query_set().filter(
            sites__id__exact=settings.SITE_ID
        )
