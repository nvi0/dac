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
            asset.title = info['title'] if info['title']!='' else file.name
            asset.mime_type = file.content_type
            asset.uid = DacUser.objects.get(user__username=username)
            asset.save()
            # get/set tags
            delim = ',' if ',' in info['tags'] else None # split by either space or comma
            tags = [tag.strip() for tag in info['tags'].split(delim)]
            for tag in tags:
                keyword = Keyword.objects.filter(text=tag)
                if keyword:
                    asset.keywords.add(keyword[0])
                else:
                    keyword = Keyword()
                    keyword.text = tag
                    keyword.save()
                    asset.keywords.add(keyword)
            
            # save file
            save_file_name = ''.join(['dacf_',str(asset.aid)])
            with open(''.join([FILE_DIR,save_file_name]), 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            

