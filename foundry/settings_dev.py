from foundry.settings import *

FOUNDRY['layers'] = ('web', 'basic',)

#TIME_ZONE = 'Africa/Johannesburg'
#USE_TZ = True

compute_settings(sys.modules[__name__])
