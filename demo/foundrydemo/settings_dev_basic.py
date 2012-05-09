from foundry import settings as foundry_settings

from foundrydemo.settings import *


FOUNDRY['layers'] = ('basic',)

foundry_settings.compute_settings(sys.modules[__name__])
