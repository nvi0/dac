from django.db import models
from django import forms

POSITIONS = (
        ('f', 'Faculty'),
        ('s', 'Staff'),
        ('u', 'Student'),
        )

class User(models.Model):
    uid = models.AutoField(primary_key=True)
    fname = models.CharField(max_length=10)
    lname = models.CharField(max_length=10)
    admin = models.BooleanField(default=False)
    position = models.CharField(max_length=1, choices=POSITIONS)
    active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('fname','lname',)

    def __unicode__(self):
        return ' '.join([self.fname,self.lname])

class Asset(models.Model):
    aid = models.AutoField(primary_key=True)
    uid = models.ForeignKey('User')
    mime_type = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    submitted = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __unicode__(self):
        return self.title

class Keyword(models.Model):
    kid = models.AutoField(primary_key=True)
    text = models.CharField(max_length=100,unique=True)
#    assets = models.ManyToManyField('Asset')

    def __unicode__(self):
        return self.text

class Asset_keyword(models.Model):
    aid = models.ForeignKey('Asset')
    kid = models.ForeignKey('Keyword')

    class Meta:
        unique_together = ('aid','kid')


class UploadFileForm(forms.Form):
    file = forms.FileField()
