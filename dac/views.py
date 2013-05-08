from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

def home(request):
    return HttpResponseRedirect('/dac/')

@login_required(redirect_field_name='')
def cas_redirect(request):
    return HttpResponseRedirect('/dac/')
    