import os
from django.core.paginator import Paginator

from dac.uploader.models import *

import logging
logger = logging.getLogger(__name__)

def handle_uploaded_file(file, asset):
    # save file
    path = asset.gen_file_path()
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

    with open(asset.gen_full_file_name(), 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

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

def is_duplicate_file(new_title):
    return (len(Asset.objects.get_by_exact_title(new_title)) != 0)
    
def get_file_list(request, perpage, page):
    m = {}
    searchcat = request.GET.get('searchcat', '')
    searchtext = request.GET.get('searchtext', '')
    if searchtext != '':
        logger.info(' '.join(['* SEARCH', searchcat, searchtext]))
        m.update({'searchcat': searchcat, 'searchtext': searchtext})

    file_list = Asset.objects.get_search_result(searchcat, searchtext)
    
    # pagination
    page = int(page)
    paginator = Paginator(file_list, perpage)
    if (page<1) or (page>paginator.num_pages):
        page = 1
    file_sublist = paginator.page(page)
    pages = list(range(1,paginator.num_pages+1))
    m.update({'file_list': file_sublist, 'pages': pages,})
    
    return m