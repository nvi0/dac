from django import forms
from models import POSITIONS

class UploadFileForm(forms.Form):
    title = forms.CharField(required=False,label='Title',max_length=30)
    file = forms.FileField(label='File')
    tags = forms.CharField(required=False,label='Tags',max_length=30)

def handle_uploaded_file(file):
    with open('/tmp/uploaded', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
