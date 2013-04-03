from django import forms
from models import *
FILE_DIR='/tmp/'


class UploadFileForm(forms.Form):
    title = forms.CharField(required=False,label='Title',max_length=30)
    file = forms.FileField(label='File')
    tags = forms.CharField(required=False,label='Tags',max_length=30)
    def handle(self, username):
        if self.is_valid():
            info = self.cleaned_data
            file = info['file']
            print ' '.join([' * Uploading file:', str(file), 'by', username])
            asset = Asset()
            asset.populate(username, info)
            # save file
            save_file_name = ''.join(['dacf_',str(asset.aid)])
            with open(''.join([FILE_DIR,save_file_name]), 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            

