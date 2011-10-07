from django.db import models
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.conf import settings

from preferences import preferences

from foundry.models import Member

class MultiBackend(ModelBackend):

    @property
    def _authentication_chain(self):
        """If specified in settings then return that, else return the
        default."""
        result = getattr(settings, 'AUTHENTICATION_CHAIN', None)
        if result is not None:
            return result
       
        # Prep result
        fieldnames = preferences.LoginPreferences.login_fields
        result = [(Member, fieldnames)]

        # Retrieve profile model if possible
        module = getattr(settings, 'AUTH_PROFILE_MODULE', None)
        if module is not None:
            app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            profile_model = models.get_model(app_label, model_name)
            result.append(profile_model, fieldnames)

        return result

    def authenticate(self, username=None, password=None):
        obj = None
        
        for klass, fieldnames in self._authentication_chain:
            for fieldname in fieldnames:
                try:
                    obj = klass.objects.get(**{fieldname:username})
                except klass.DoesNotExist:
                    pass
                else:
                    break
            if obj is not None:
                break
        
        if obj is None:
            return None

        # Obj is an instance of either user or a subclass of user, or else a
        # profile. 
        if isinstance(obj, User):
            user = obj
        else:
            user = obj.user
                           
        if user.check_password(password):
            return user
        
        return None

    def get_user(self, user_id):
        """Return an instance of either user or a subclass of user"""
        for klass, fieldnames in self._authentication_chain:
            if issubclass(klass, User):
                try:
                    return klass.objects.get(pk=user_id)
                except klass.DoesNotExist:
                    pass
        return None
