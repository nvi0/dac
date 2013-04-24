import logging
import os
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.core.servers.basehttp import FileWrapper

from forms import UploadFileForm
from models import *
from helpers import *

logger = logging.getLogger(__name__)
URL_INDEX = '/dac/'
URL_PERSONAL = '/dac/personal/'

@login_required
def index(request):
    handle_new_user(request.user)
    m = get_file_list(request)
    form = UploadFileForm()
    m.update(csrf(request))
    m.update({'form': form})
    m.update(update_searchcat(request.GET.get('searchcat', '')))
    
    #c = RequestContext(request, {'dac_user':get_dac_user(request.user.username)})
    m.update({'dac_user':get_dac_user(request.user.username)})
    return render(request, 'uploader/index.html', m)

@login_required 
def upload_file(request):
    """ 
    Handle ajax form submit, return json.
    """
    if request.method == 'POST':
        if is_student(request.user.username):
            # TODO: display error message?
            return HttpResponseRedirect(URL_INDEX)
            
        # handle upload    
        form = UploadFileForm(request.POST, request.FILES)
        response_data = form.handle(request.user.username)
        if response_data['non_existed']:
            # include uploaded data into response_data
            newfile_html = render_to_string("uploader/one_file_row.html", {'fileinfo': response_data['asset']})
            response_data.update({'newfile': newfile_html })
            response_data.pop('asset', None)
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    return HttpResponseRedirect(URL_INDEX)

@login_required
def confirm_upload_file(request):
    """
    Handle ajax confirm post.
    Rename temporary saved file to correct file name.
    """
    if request.method == 'POST':
        if is_student(request.user.username):
            # TODO: display error message?
            return HttpResponseRedirect(URL_INDEX)
            
        if request.POST.get('overwrite') == 'true':
            handle_confirmed_duplicated_file(request.user, request.POST.get('aid'), request.POST.get('new_mime_type'), request.POST.get('new_nice_type'))
        else:
            handle_canceled_duplicated_file(request.user, request.POST.get('aid'))
    return HttpResponseRedirect(URL_INDEX)

@login_required
def manage_file(request):
    if is_student(request.user.username):
        # TODO: display error message?
        return HttpResponseRedirect(URL_INDEX)
        
    searchcat = request.GET.get('searchcat', '')
    searchtext = request.GET.get('searchtext', '')
    if searchtext != '':
        logger.info(' '.join(['* SEARCH', searchcat, searchtext]))
        file_list = Asset.objects.get_search_result(searchcat, searchtext).filter(uid__user=request.user)
    else:
        file_list = Asset.objects.get_by_user(request.user.username)
    
    form = UploadFileForm()
    m = {'file_list': file_list, 'form': form}
    m.update(update_searchcat(searchcat))
   
    m.update(csrf(request))
    m.update({'dac_user':get_dac_user(request.user.username)})
    
    return render(request, 'uploader/manage_file.html', m)

@login_required
def delete_one_file(request,aid):
    if is_student(request.user.username):
        # TODO: display error message?
        return HttpResponseRedirect(URL_INDEX)
        
    handle_delete_file(request.user,aid)
    return HttpResponseRedirect(URL_PERSONAL)

@login_required
def delete_selected_files(request):
    if is_student(request.user.username):
        # TODO: display error message?
        return HttpResponseRedirect(URL_INDEX)
        
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
