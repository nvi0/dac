from django import forms
from models import *
from helpers import handle_uploaded_file

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
        existed_asset = Asset.objects.get_by_exact_title(new_title)
        if existed_asset:
            logger.info(' '.join(['* Unsuccessful uploading duplicated file:', file_name, ]))
            # Store temporary file
            handle_uploaded_file(cleaned_data['file'], existed_asset[0])
            cleaned_data.update({'aid': existed_asset[0].aid})
        return cleaned_data
        
    def handle(self, username):
        if self.is_valid():
            info = self.cleaned_data
            # existed asset
            if 'aid' in info:
                return False, info['aid']
        
            # success adding new asset
            asset = Asset()
            asset.populate(username, info)
            handle_uploaded_file(info['file'], asset)
            return asset, asset.aid
        