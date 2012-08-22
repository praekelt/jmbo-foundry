from foundry.settings import *

#FOUNDRY['layers'] =  ('web', 'basic',)
FOUNDRY['layers'] =  ('smart', 'mid', 'basic',)


compute_settings(sys.modules[__name__])
