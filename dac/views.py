from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required

from helpers import RegistrationForm, UploadFileForm, handle_uploaded_file, handle_registration

@login_required
def home(request):
    user_agent = request.META.get("HTTP_USER_AGENT", None)
    ip = request.META.get('REMOTE_ADDR', None)
    return render(request, 'home.html', {
        'user_agent': user_agent,
        'ip': ip,
    })

def fooview(request, foo_id):
    return HttpResponse('from fooview. %s' % foo_id)

@login_required
def uploadfile(request):
    if request.method == 'POST':
        # a = request.POST
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()

    c = {'form': form}
    c.update(csrf(request))
    return render_to_response('uploadfile.html', c)

@login_required
def profile(request):
    return render(request, 'profile.html')
    
def registration(request):
    if request.method == 'POST':
        # handle registration info
        form = RegistrationForm(request.POST)
        # print(form.__dict__)
        if form.is_valid():
            handle_registration(form.data)
            return render_to_response('registration/registration_complete.html')
    else:
        form = RegistrationForm()
    
    c = {'form': form}
    c.update(csrf(request))
    return render_to_response('registration/registration_form.html', c)