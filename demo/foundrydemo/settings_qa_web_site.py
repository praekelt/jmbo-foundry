from foundry import settings as foundry_settings

from foundrydemo.settings_live_base import *


FOUNDRY['layers'] = ('web', 'basic',)

foundry_settings.compute_settings(sys.modules[__name__])
