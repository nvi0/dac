import os
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

