import os
from datetime import date
from dac.uploader.models import *
FILE_DIR = '/tmp'


def handle_uploaded_file(file, assetid):
    # save file
    path = _gen_file_path()

    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

    save_file_name = ''.join(['dacf_', str(assetid)])
    with open('/'.join([path, save_file_name]), 'wb+') as destination:
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

    print ' * Deleting file',asset.str_filename(),'of user', user.username
    # asset.delete()
    # cascade keyword
    # delete file



def _gen_file_path():
    now = date.today()
    return '/'.join([FILE_DIR, str(now.year), str(now.month)])
