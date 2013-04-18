import os

from dac.uploader.models import *

import logging
logger = logging.getLogger(__name__)

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

def handle_confirmed_duplicated_file(user, aid):
    """
    Rename temporary file name to correct name.
    """
    asset = Asset.objects.get(pk=aid)
    if not asset:
        return
    
    owner = asset.uid.user
    if user != owner:
        # raise permission message
        return
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
    
    # TODO: asset.updated

def handle_canceled_duplicated_file(user, aid):
    """
    Remove temporary file.
    """
    asset = Asset.objects.get(pk=aid)
    if not asset:
        return
    
    owner = asset.uid.user
    if user != owner:
        # raise permission message
        return
    full_file_name = asset.gen_full_file_name()
    tmp_file_name = ''.join([full_file_name,'_tmp'])
    if not os.path.isfile(tmp_file_name):
        logger.warning(' '.join(['* Overwrite-no requested with non existed tmp file:', tmp_file_name, 'by', username]))
        return

    logger.info(' '.join(['* Removing tmp file:', asset.title, 'by', user.username]))
    os.remove(tmp_file_name)
    logger.info(' '.join(['* Sucessfully removed tmp file:', asset.title]))

def handle_delete_file(user, aid):
    asset = Asset.objects.get(pk=aid)
    if not asset:
        # raise error message
        return

    owner = asset.uid.user
    if user != owner:
        # raise not permission message
        return

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