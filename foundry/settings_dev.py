from foundry.settings import *

FOUNDRY['layers'] =  ('basic',)
#FOUNDRY['layers'] =  ('web', 'basic',)
#FOUNDRY['layers'] =  ('mid', 'basic',)
#FOUNDRY['layers'] =  ('smart', 'mid', 'basic',)


compute_settings(sys.modules[__name__])
