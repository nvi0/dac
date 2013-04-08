import logging
import os
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.core.servers.basehttp import FileWrapper

from forms import UploadFileForm
from models import *
from helpers import handle_delete_file

logger = logging.getLogger(__name__)
URL_INDEX = '/viewfiles/'
URL_PERSONAL = '/viewfiles/personal/'

@login_required
def index(request):
    searchcat = request.GET.get('searchcat', '')
    searchtext = request.GET.get('searchtext', '')
    if searchtext != '':
        logger.info(' '.join(['* SEARCH', searchcat, searchtext]))

    file_list = Asset.objects.get_search_result(searchcat, searchtext)
    form = UploadFileForm()
    m = {'file_list': file_list, 'form': form}
    m.update(csrf(request))
    return render(request, 'uploader/index.html', m)


def fooview(request, foo_id):
    return HttpResponse('from fooview. %s' % foo_id)


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        form.handle(request.user.username)

    return HttpResponseRedirect(URL_INDEX)


@login_required  # TODO: faculty/staff only
def manage_file(request):
    
    searchcat = request.GET.get('searchcat', '')
    searchtext = request.GET.get('searchtext', '')
    if searchtext != '':
        logger.info(' '.join(['* SEARCH', searchcat, searchtext]))
        file_list = Asset.objects.get_search_result(searchcat, searchtext).filter(uid__user=request.user)
    else:
        file_list = Asset.objects.get_by_user(request.user.username)
    
    form = UploadFileForm()
    m = {'file_list': file_list, 'form': form}
    m.update(csrf(request))
    return render(request, 'uploader/manage_file.html', m)

@login_required
def delete_one_file(request,aid):
    handle_delete_file(request.user,aid)
    return HttpResponseRedirect(URL_PERSONAL)

@login_required
def delete_selected_files(request):
    if request.method == 'POST':
        for k,v in request.POST.items():
            if v == 'on':
                try:
                    handle_delete_file(request.user, int(k))
                except ValueError:
                    pass
    return HttpResponseRedirect(URL_PERSONAL)

@login_required
def send_one_file(request,aid):
    """                                                                         
    Send a file through Django without loading the whole file into              
    memory at once. The FileWrapper will turn the file object into an           
    iterator for chunks of 8KB.                                                 
    """
    asset = Asset.objects.get(pk=aid)
    if not asset:
        # raise not found message
        return HttpResponseRedirect(URL_INDEX)

    filename = asset.gen_full_file_name()
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type=asset.mime_type)
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename={nice_filename}'.format(nice_filename=asset.str_filename())
    return response
