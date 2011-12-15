from django.conf import settings

def foundry(request):
    return {
        'FOUNDRY': settings.FOUNDRY,
    }
