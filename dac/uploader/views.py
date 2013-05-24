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
import ldap_getter

logger = logging.getLogger(__name__)
URL_INDEX = '/dac/'
URL_PERSONAL = '/dac/personal/'
URL_INTROPAGE = '/dac/login/'
URL_ADMIN = '/dac/admin/'

def intropage(request):
    return render(request, 'uploader/intropage.html')

@login_required(login_url=URL_INTROPAGE, redirect_field_name='')
def index(request):
    handle_new_user(request.user.username)
    m = get_file_list(request)
    form = UploadFileForm()
    m.update(csrf(request)) #TODO: seems like ajaxpreset in main.js covers this?
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
            return
            
        # handle upload    
        form = UploadFileForm(request.POST, request.FILES)
        response_data = form.handle(request.user.username)
        if response_data['non_existed']:
            # include uploaded data into response_data
            newfile_html = render_to_string("uploader/one_file_row.html", {'fileinfo': response_data['asset']})
            response_data.update({'newfile': newfile_html })
            response_data.pop('asset', None)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required
def confirm_upload_file(request):
    """
    Handle ajax confirm post.
    Rename temporary saved file to correct file name OR remove temporary file.
    """
    if request.method == 'POST':
        if is_student(request.user.username):
            return
            
        if request.POST.get('overwrite') == 'true':
            handle_confirmed_duplicated_file(request.user, 
                                             request.POST.get('aid'), 
                                             request.POST.get('new_mime_type'), 
                                             request.POST.get('new_nice_type'), 
                                             request.POST.get('new_keywords'))
        else:
            handle_canceled_duplicated_file(request.user, request.POST.get('aid'))

@login_required
def manage_file(request):
    if is_student(request.user.username):
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
        return HttpResponseRedirect(URL_INDEX)
        
    handle_delete_file(request.user,aid)
    return HttpResponseRedirect(URL_PERSONAL)

@login_required
def delete_selected_files(request):
    if is_student(request.user.username):
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
    asset = get_asset(aid)
    if not asset:
        # raise not found message
        return HttpResponseRedirect(URL_INDEX)

    filename = asset.gen_full_file_name()
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type=asset.mime_type)
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename={nice_filename}'.format(nice_filename=asset.str_filename())
    return response

@login_required
def edit_tag(request):
    """
    Handle ajax post to edit tag, format:  id=elements_id&value=user_edited_content
    """
    if is_student(request.user.username):
        return
        
    if request.method != 'POST':
        return
    
    aid = request.POST.get('id','')[3:] #ex: et_183
    new_value = request.POST.get('value','')
    
    asset = get_asset(aid)
    if not asset:
        logger.warning('Request to edit tags for non-existed file, aid= {aid}'.format(aid=aid))
        return
    # TODO: check owner
    
    asset.set_keywords(new_value)
    return HttpResponse(asset.str_keywords(), content_type="text/plain")

@login_required
def edit_title(request):
    """
    Handle ajax post check for existed title
    """
    if is_student(request.user.username):
        return
        
    if request.method != 'POST':
        return
    
    aid = request.POST.get('id','')[7:] #ex: etitle_183
    new_title = request.POST.get('new_title','')
    
    asset = get_asset(aid)
    if not asset:
        logger.warning('Request to edit title for non-existed file, aid= {aid}'.format(aid=aid))
        return

    m = {'id': request.POST.get('id',''), 'new_title': new_title, 'old_title': asset.title}
    # TODO: check owner
    if asset.set_title(new_title):
        m.update({'saved':True,'existed':False})
        return HttpResponse(json.dumps(m), content_type="application/json")
        
    m.update({'saved':False,'existed':True})
    return HttpResponse(json.dumps(m), content_type="application/json")

@login_required #TODO: admin only
def admin(request):
#    m = {'user_list': DacUser.objects.order_by('position')} # conveniently 'u' is after 'f' and 's'
    m = get_user_list(request)
    m.update({'dac_user':get_dac_user(request.user.username)})
    return render(request, 'uploader/admin.html', m)

@login_required #TODO: admin only
def admin_edit_positions(request):
    if request.method != 'POST':
        return HttpResponseRedirect(URL_ADMIN)
    print request.POST
    for k,v in request.POST.items():
        if 'ps_' in k: # process new position
            try:
                save_new_position(int(k[3:]),v)
            except ValueError:
                pass
    return HttpResponseRedirect(URL_ADMIN)

@login_required #TODO: admin only
def admin_create_user(request):
    """
    Handle ajax post.
    """
    if is_student(request.user.username):
        return
    if request.method != 'POST':
        return
    
    new_username = request.POST['username']
    if new_username == '':
        return
    
    position = request.POST.get('position','')
    if position not in ('f','s'):
        return

    print(request.POST)
    
    if DacUser.objects.filter(user__username=new_username):
        return HttpResponse(json.dumps({'success':False, 'reason':'existed'}), content_type="application/json")
    
    user_info = ldap_getter.get_user_info(new_username)
    if user_info == None:
        return HttpResponse(json.dumps({'success':False, 'reason':'no_ldap_record'}), content_type="application/json")

    handle_new_user(new_username, user_info, request.POST['position'])
    return HttpResponse(json.dumps({'success':True}), content_type="application/json")
    