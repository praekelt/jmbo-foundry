import os

from django.conf import settings
from django.template.loaders.app_directories import Loader
from django.template.base import TemplateDoesNotExist


class AppDirectoriesTypeLoader(Loader):

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Affixes the TEMPLATE_TYPE setting value to the template name thus
        allowing for template switching.
        """     
        template_name = os.path.join(settings.FOUNDRY['layers'][0], template_name)
        return super(AppDirectoriesTypeLoader, self).get_template_sources(
            template_name, template_dirs
        )
