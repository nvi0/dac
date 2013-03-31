from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required

from helpers import RegistrationForm, UploadFileForm, handle_uploaded_file, handle_registration
from models import *

CATEGORIES = {'ti':'title','ty':'mime_type','us':'uid','ta':'kid'}

@login_required
def home(request):
    searchcat = request.GET.get('searchcat','')
    searchtext = request.GET.get('searchtext','')
    if searchtext != '':
        print ' * SEARCH',searchcat,searchtext
    # filter
    file_list = Asset.objects.all()
    form = UploadFileForm()
    m = {'file_list': file_list, 'form': form}
    m.update(csrf(request))
    return render(request,'home.html', m)

def fooview(request, foo_id):
    return HttpResponse('from fooview. %s' % foo_id)

@login_required
def uploadfile(request):
    if request.method == 'POST':
        # a = request.POST
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print ' * Uploading file:',request.FILES['file']
            handle_uploaded_file(request.FILES['file'])
    return HttpResponseRedirect('/')

@login_required
def manage_file(request):
    return render(request, 'manage_file.html')
    
def registration(request):
    if request.method == 'POST':
        # handle registration info
        form = RegistrationForm(request.POST)
        # print(form.__dict__)
        if form.is_valid():
            handle_registration(form.cleaned_data)
            form.clean
            return render_to_response('registration/registration_complete.html')
    else:
        form = RegistrationForm()
    
    c = {'form': form}
    c.update(csrf(request))
    return render_to_response('registration/registration_form.html', c)

def fileview(request):
    # process restraint
    
    file_list = Asset.objects.all()
    m = {'file_list': file_list}
    return render_to_response('filestable.html', m)