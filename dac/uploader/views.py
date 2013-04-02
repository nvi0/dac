from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required

from forms import UploadFileForm, handle_uploaded_file
from models import *

@login_required
def index(request):
    searchcat = request.GET.get('searchcat','')
    searchtext = request.GET.get('searchtext','')
    if searchtext != '':
        print ' * SEARCH',searchcat,searchtext
    
    file_list = Asset.objects.get_search_result(searchcat,searchtext)
    form = UploadFileForm()
    m = {'file_list': file_list, 'form': form}
    m.update(csrf(request))
    return render(request,'uploader/index.html', m)

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
    return render(request, 'uploader/manage_file.html')
    
def fileview(request):
    # process restraint
    
    file_list = Asset.objects.all()
    m = {'file_list': file_list}
    return render_to_response('uploader/filestable.html', m)
