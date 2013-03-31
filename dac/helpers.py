from django import forms
from models import POSITIONS

class UploadFileForm(forms.Form):
    file = forms.FileField()

class RegistrationForm(forms.Form):
    username = forms.CharField(required=True,label='Username',max_length=30)
    password = forms.CharField(required=True,label='Password',max_length=30,min_length=6)
    first_name = forms.CharField(required=True,label='First name',max_length=30)
    last_name = forms.CharField(required=True,label='Last name',max_length=30)
    email = forms.EmailField(required=True,label='Email')
    position = forms.ChoiceField(POSITIONS)

def handle_uploaded_file(file):
    with open('/tmp/uploaded', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def handle_registration(data):
    print(data.get('username'))