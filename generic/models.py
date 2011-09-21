from django.core.urlresolvers import reverse
from django.db import models

from preferences.models import Preferences


class FooterMenuLink(models.Model):
    title = models.CharField(
        max_length=256,
        help_text='A short descriptive title.',
    )
    view_name = models.CharField(
        max_length=256,
        help_text="View name to which this link will redirect. This takes precedence over url field below.",
        blank=True,
        null=True,
    )
    url = models.CharField(
        max_length=256,
        help_text='URL to which this menu link will redriect.',
        blank=True,
        null=True,
    )
        
    class Meta():
        ordering = ('footermenulinkposition__position',)

    def get_absolute_url(self):
        if self.view_name:
            return reverse(self.view_name)
        else:
            return self.url

    def __unicode__(self):
        return self.title


class FooterMenuPreferences(Preferences):
    __module__ = 'preferences.models'
    links = models.ManyToManyField(FooterMenuLink, through='generic.FooterMenuLinkPosition')


class FooterMenuLinkPosition(models.Model):
    preferences = models.ForeignKey(FooterMenuPreferences)
    link = models.ForeignKey(FooterMenuLink)
    position = models.IntegerField()

    class Meta():
        ordering = ('position',)

    def __unicode__(self):
        return "Link titled %s in position %s." % (self.link.title, self.position)


    

