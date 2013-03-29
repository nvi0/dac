from django.db import models
from django.contrib.auth.models import User

POSITIONS = (
        ('f', 'Faculty'),
        ('s', 'Staff'),
        ('u', 'Student'),
        )

class DacUser(models.Model):
    user = models.OneToOneField(User)
    position = models.CharField(max_length=1, choices=POSITIONS)
    # first_name = models.CharField(max_length=30)
    # last_name = models.CharField(max_length=30)
    
    # class Meta:
    #    unique_together = ('first_name','last_name',)

    def __unicode__(self):
        return self.user.username

class Asset(models.Model):
    aid = models.AutoField(primary_key=True)
    uid = models.ForeignKey('DacUser')
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



