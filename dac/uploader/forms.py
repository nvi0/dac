from django import forms
from models import *
from helpers import handle_uploaded_file, is_duplicate_file

import logging
logger = logging.getLogger(__name__)


class UploadFileForm(forms.Form):
    title = forms.CharField(required=False, label='Title', max_length=30)
    file = forms.FileField(label='File')
    tags = forms.CharField(required=False, label='Tags', max_length=30)
    
    def clean(self): # implicitly invoked by self.is_valid()
        cleaned_data = super(UploadFileForm, self).clean()
        
        # check if file is not empty
        try:
            file_name = cleaned_data['file'].name
        except KeyError:
            raise forms.ValidationError("Empty file")
        
        # check if file is duplicated
        new_title = cleaned_data['title'] if cleaned_data['title'] != '' else file_name
        if is_duplicate_file(new_title):
            logger.info(' '.join(['* Unsuccessful uploading duplicated file:', file_name, ]))
            raise forms.ValidationError("Existed file") # TODO: ask to rewrite
        
        return cleaned_data
        
    def handle(self, username):
        if self.is_valid():
            info = self.cleaned_data
            logger.info(' '.join(['* Uploading file:', info['file'].name, 'by', username]))
            asset = Asset()
            asset.populate(username, info)
            handle_uploaded_file(info['file'], asset)
