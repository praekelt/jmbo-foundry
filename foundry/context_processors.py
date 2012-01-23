from django.conf import settings

def foundry(request):
    return {
        'FOUNDRY': settings.FOUNDRY,
        'LAYER_PATH': settings.FOUNDRY['layers'][0] + '/'
    }
