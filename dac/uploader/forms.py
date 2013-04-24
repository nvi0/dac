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
        
        new_file = cleaned_data['file']
        # check if file is duplicated
        new_title = cleaned_data['title'] if cleaned_data['title'] != '' else file_name
        existed_asset = Asset.objects.get_by_exact_title(new_title)
        if existed_asset:
            logger.info(' '.join(['* User uploading duplicated file:', new_title, ]))
            cleaned_data.update({'asset': existed_asset[0]})
            
            cleaned_data.update({'new_mime_type': new_file.content_type})
            
            ori_type = new_file.name[new_file.name.rfind('.')+1:]
            new_nice_type = ori_type if len(ori_type) <= 4 else 'unknown'
            cleaned_data.update({'new_nice_type': new_nice_type})
        return cleaned_data
        
    def handle(self, username):
        if self.is_valid():
            info = self.cleaned_data
            # existed asset
            if 'asset' in info:
                if info['asset'].uid.user.username == username:
                    # Store temporary file
                    handle_uploaded_file(info['file'], info['asset'], is_final=False)
                return {'non_existed': False, 'aid': info['asset'].aid, 'owner': info['asset'].uid.user.username,
                        'new_mime_type': info['new_mime_type'], 'new_nice_type': info['new_nice_type'],
                        'is_existed_owner': info['asset'].uid.user.username == username}
        
            # success adding new asset
            asset = Asset()
            asset.populate(username, info)
            handle_uploaded_file(info['file'], asset, is_final=True)
            return {'non_existed': True, 'asset': asset, 'aid': asset.aid}
        