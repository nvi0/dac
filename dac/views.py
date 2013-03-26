from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.core.context_processors import csrf
from models import UploadFileForm

def home(request):
    user_agent = request.META.get("HTTP_USER_AGENT", None)
    ip = request.META.get('REMOTE_ADDR', None)
    return render(request, 'home.html', {
        'user_agent': user_agent,
        'ip': ip,
    })

def fooview(request, foo_id):
    return HttpResponse('from fooview. %s' % foo_id)

def uploadfile(request):
    if request.method == 'POST':
        a = request.POST
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()

    c = {'form': form}
    c.update(csrf(request))
    return render_to_response('uploadfile.html', c)    

def handle_uploaded_file(file):
    with open('/tmp/uploaded', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
