from django import forms
from models import *
from helpers import handle_uploaded_file

import logging
logger = logging.getLogger(__name__)


class UploadFileForm(forms.Form):
    title = forms.CharField(required=False, label='Title', max_length=30)
    file = forms.FileField(label='File')
    tags = forms.CharField(required=False, label='Tags', max_length=30)

    def handle(self, username):
        if self.is_valid():
            info = self.cleaned_data
            logger.info(' '.join(['* Uploading file:', str(file), 'by', username]))
            asset = Asset()
            asset.populate(username, info)
            handle_uploaded_file(info['file'], asset)
