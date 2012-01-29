import os

from django.conf import settings
from django.template.loaders.app_directories import Loader, app_template_dirs
from django.template.base import TemplateDoesNotExist
from django.utils._os import safe_join


class AppDirectoriesTypeLoader(Loader):

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Prefix template_name with layer in use thus enabling template 
        switching. Override entire method since original uses a generator 
        and the extra for loop required introduces syntax complexity.
        """     
        '''
        Original: keep as reference
        template_name = os.path.join(settings.FOUNDRY['layers'][0], template_name)
        return super(AppDirectoriesTypeLoader, self).get_template_sources(
            template_name, template_dirs
        )
        '''

        if not template_dirs:
            template_dirs = app_template_dirs
        for template_dir in template_dirs:
            for layer in settings.FOUNDRY['layers']:
                l_template_name = os.path.join(layer, template_name)
                try:
                    yield safe_join(template_dir, l_template_name)
                except UnicodeDecodeError:
                    # The template dir name was a bytestring that wasn't valid UTF-8.
                    raise
                except ValueError:
                    # The joined path was located outside of template_dir.
                    pass
