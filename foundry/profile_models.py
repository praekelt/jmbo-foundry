"""
We are not yet ready to rename django-profile, so copy and paste models.
"""
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models

from photologue.models import ImageModel

class AbstractProfileBase(models.Model):
    class Meta:
        abstract = True

    user = models.ForeignKey(
        User, 
        unique=True
    )
    
    def __unicode__(self):
        return self.user.username
    
class AbstractAvatarProfile(ImageModel):
    class Meta:
        abstract = True

class AbstractSocialProfile(models.Model):
    class Meta:
        abstract = True
    
    facebook_id = models.CharField(
        verbose_name=_('Facebook ID'),
        max_length=128,
        blank=True, 
        null=True,
    )
    twitter_username = models.CharField(
        verbose_name=_('Twitter username'),
        max_length=128,
        blank=True,
        null=True,
    )

    @property
    def facebook_url(self):
        if self.facebook_id:
            return "http://www.facebook.com/profile.php?id=%s" % self.facebook_id
        else:
            return None
    
    @property
    def twitter_url(self):
        if self.twitter_username:
            return "http://www.twitter.com/%s" % self.twitter_username
        else:
            return None

class AbstractLocationProfile(models.Model):
    class Meta:
        abstract = True
    
    address = models.TextField(
        verbose_name=_('Address'),
        blank=True,
        null=True,
    )
    city = models.CharField(
        verbose_name=_('City'),
        max_length=256,
        blank=True,
        null=True,
    )
    zipcode = models.CharField(
        verbose_name=_('Zipcode'),
        max_length=32,
        blank=True,
        null=True,
    )
    province = models.CharField(
        verbose_name=_('Province'),
        max_length=256,
        blank=True,
        null=True,
    )

class AbstractPersonalProfile(models.Model):
    class Meta:
        abstract = True
    
    dob = models.DateField(
        verbose_name=_("Date of Birth"),
        blank=True,
        null=True,
    )
    
    gender = models.CharField(
        verbose_name=_("Gender"),
        max_length=1,
        blank=True,
        null=True,
        choices=(
            ('F', _('Female')),
            ('M', _('Male')),
        )
    )

    about_me = models.TextField(
        verbose_name=_("About me"),
        blank=True,
        null=True,                                
    )

class AbstractContactProfile(models.Model):
    class Meta:
        abstract = True
   
    mobile_number = models.CharField(
        verbose_name=_("Mobile number"),
        max_length=64,
        blank=True,
        null=True,
    )

class AbstractSubscriptionProfile(models.Model):
    class Meta:
        abstract = True
    
    receive_sms = models.BooleanField(
        verbose_name=_("Receive sms"),
        default=False,
    )
    receive_email = models.BooleanField(
        verbose_name=_("Receive email"),
        default=False,
    )

class AbstractWebuserProfile(AbstractProfileBase, AbstractAvatarProfile, AbstractContactProfile, AbstractLocationProfile, AbstractPersonalProfile, AbstractSocialProfile, AbstractSubscriptionProfile):
    class Meta:
        abstract = True
