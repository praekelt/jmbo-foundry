from django.db import models
from django.contrib.sites.models import get_current_site


class CachingMixin(models.Model):
    enable_caching = models.BooleanField(default=False, null=False)
    cache_type = models.CharField(
        max_length=32,
        default='all_users',
        choices=(
            ('all_users', 'All users'),
            ('anonymous_only', 'Anonymous only'),
            ('anonymous_and_authenticated', 'Anonymous and authenticated'),
            ('per_user', 'Per user'),
        ),
        help_text="""All users - content is cached once for all users
<br />
Anonymous only - content is cached once only for anonymous users
<br />
Anonymous and authenticated - content is cached once for anonymous users and \
once for authenticated users
<br />
Per user - content is cached once for anonymous users and for each \
authenticated user individually"""
    )
    cache_timeout = models.PositiveIntegerField(
        default=60, 
        help_text="Timeout in seconds"
    )

    class Meta:
        abstract = True
