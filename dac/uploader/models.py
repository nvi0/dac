from django.db import models
from django.contrib.auth.models import User

POSITIONS = (
        ('f', 'Faculty'),
        ('s', 'Staff'),
        ('u', 'Student'),
        )
CATEGORIES = {'ti':'title','ty':'mime_type','us':'uid','ta':'kid'}

class DacUser(models.Model):
    user = models.OneToOneField(User)
    position = models.CharField(max_length=1, choices=POSITIONS)

    def __unicode__(self):
        return self.user.username

class AssetManager(models.Manager):
    def get_search_result(self,searchcat,searchtext):
        if searchcat=='ti':
            return super(AssetManager, self).get_query_set().filter(title__icontains=searchtext)
        elif searchcat=='ty':
            return super(AssetManager, self).get_query_set().filter(mime_type__iexact=searchtext)
        elif searchcat=='us':
            return super(AssetManager, self).get_query_set().filter(uid__user__username__icontains=searchtext)
        elif searchcat=='ta':
            result = set()
            searchkeywords = Keyword.objects.filter(text__icontains=searchtext)
            for searchkeyword in searchkeywords:
                result.update(searchkeyword.asset_set.all())
            return list(result)
        

class Asset(models.Model):
    objects = AssetManager()
    
    aid = models.AutoField(primary_key=True)
    uid = models.ForeignKey('DacUser')
    mime_type = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    submitted = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    keywords = models.ManyToManyField('Keyword')
    
    def __unicode__(self):
        return self.title
    def str_keywords(self):
        return ', '.join(keyword.text for keyword in self.keywords.all())

    
        
class Keyword(models.Model):
    kid = models.AutoField(primary_key=True)
    text = models.CharField(max_length=100,unique=True)

    def __unicode__(self):
        return self.text

