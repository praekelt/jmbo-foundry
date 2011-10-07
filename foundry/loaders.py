import os

from django.conf import settings
from django.template.loaders.app_directories import Loader


class TypeLoader(Loader):

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Affixes the TEMPLATE_TYPE setting value to the template name thus
        allowing for template switching.
        """
        template_name = os.path.join(settings.TEMPLATE_TYPE, template_name)
        return super(TypeLoader, self).get_template_sources(template_name, \
                template_dirs)
