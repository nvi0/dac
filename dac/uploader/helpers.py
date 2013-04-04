import os
from datetime import date
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


def _gen_file_path():
    now = date.today()
    return '/'.join([FILE_DIR, str(now.year), str(now.month)])
