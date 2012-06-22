from foundry import settings as foundry_settings

from foundrydemo.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

FOUNDRY['layers'] = ('web', 'basic',)

foundry_settings.compute_settings(sys.modules[__name__])
