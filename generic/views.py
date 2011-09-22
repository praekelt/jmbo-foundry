from django.http import HttpResponseRedirect 
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, get_backends
from django.conf import settings

from generic.forms import JoinForm

def join(request):
    """Surface join form"""
    if request.method == 'POST':
        form = JoinForm(request.POST, request.FILES) 
        if form.is_valid():
            user = form.save()
            backend = get_backends()[0]
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, user)            
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = JoinForm() 

    extra = dict(form=form)
    return render_to_response('generic/join.html', extra, context_instance=RequestContext(request))

