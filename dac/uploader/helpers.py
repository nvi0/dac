import os

from dac.uploader.models import *

import logging
logger = logging.getLogger(__name__)


class PermissionError(Exception):
    pass
    
    
def is_student(username):
    try:
        dac_user = DacUser.objects.get(user__username=username)
    except ObjectDoesNotExist:
        return False
    
    return dac_user.is_student()
    
def get_dac_user(username):
    try:
        dac_user = DacUser.objects.get(user__username=username)
    except ObjectDoesNotExist:
        return None
    return dac_user

def get_asset(aid):
    try:
        asset = Asset.objects.get(pk=int(aid))
    except ValueError, TypeError:
        return None
    except ObjectDoesNotExist:
        return None
    return asset

def handle_uploaded_file(file, asset, is_final):
    """
    Save file to temporary place.
    """
    path = asset.gen_file_path()
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

    save_file_name = ''.join([asset.gen_full_file_name(),'_tmp']) if not is_final else ''.join([asset.gen_full_file_name()])
    with open(save_file_name, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    if is_final:
        logger.info(' '.join(['* Sucessfully saved file:', asset.title]))

def handle_confirmed_duplicated_file(user, aid, new_mime_type, new_nice_type):
    """
    Rename temporary file name to correct name.
    """
    asset = get_asset(aid)
    if not asset:
        return
    
    owner = asset.uid.user
    if user != owner:
        raise PermissionError()
        
    full_file_name = asset.gen_full_file_name()
    tmp_file_name = ''.join([full_file_name,'_tmp'])
    if not os.path.isfile(tmp_file_name):
        logger.warning(' '.join(['* Overwrite-yes requested with non existed tmp file:', tmp_file_name, 'by', username]))
        return

    logger.info(' '.join(['* Saving file:', asset.title, 'by', user.username]))
    try:
        # delete previous file if any
        os.remove(full_file_name)
    except OSError:
        pass
    os.rename(tmp_file_name,full_file_name)
    logger.info(' '.join(['* Sucessfully saved file:', asset.title]))
    
    asset.populate_overwrite(new_mime_type, new_nice_type)

def handle_canceled_duplicated_file(user, aid):
    """
    Remove temporary file.
    """
    asset = get_asset(aid)
    if not asset:
        return
    
    owner = asset.uid.user
    if user != owner:
        raise PermissionError()
        
    full_file_name = asset.gen_full_file_name()
    tmp_file_name = ''.join([full_file_name,'_tmp'])
    if not os.path.isfile(tmp_file_name):
        logger.warning(' '.join(['* Overwrite-no requested with non existed tmp file:', tmp_file_name, 'by', username]))
        return

    logger.info(' '.join(['* Removing tmp file:', asset.title, 'by', user.username]))
    os.remove(tmp_file_name)
    logger.info(' '.join(['* Sucessfully removed tmp file:', asset.title]))

def handle_delete_file(user, aid):
    """
    Delete stored file and entry in table asset.
    """
    asset = get_asset(aid)
    if not asset:
        return

    owner = asset.uid.user
    if user != owner:
        raise PermissionError()

    logger.info(' '.join(['* Deleting file',asset.str_filename(),'of user', user.username]))

    # delete file
    full_file_name = asset.gen_full_file_name()
    try:
        os.remove(full_file_name)
    except OSError:
        logger.warning('Attempt to delete non-existent file at {p}'.format(p=full_file_name))

    asset.delete()
    # TODO: cascade keyword

    
def get_file_list(request):
    m = {}
    searchcat = request.GET.get('searchcat', '')
    searchtext = request.GET.get('searchtext', '')
    if searchtext != '':
        logger.info(' '.join(['* SEARCH', searchcat, searchtext]))
        m.update({'searchcat': searchcat, 'searchtext': searchtext})
    
    file_list = Asset.objects.get_search_result(searchcat, searchtext)
    
    m.update({'file_list': file_list})
    
    return m
    
def update_searchcat(searchcat):
    d = {'ti_selected':'', 'ty_selected':'', 'us_selected': '', 'ta_selected':''}
    if searchcat != '':
        d.update({''.join([searchcat,'_selected']): 'selected'})
    return d
    
def handle_new_user(new_user):
    if DacUser.objects.filter(user__username=new_user.username):
        return # nothing to do
    logger.info('Creating new user logged in from CAS: {username}'.format(username=new_user.username))
    dac_user = DacUser()
    dac_user.populate(new_user.username)
