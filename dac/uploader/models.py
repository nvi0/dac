import mimetypes
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from dac.settings import FILE_DIR

POSITIONS = (
    ('f', 'Faculty'),
    ('s', 'Staff'),
    ('u', 'Student'),
)
CATEGORIES = {'ti': 'title', 'ty': 'mime_type', 'us': 'uid', 'ta': 'kid'}

class DacUser(models.Model):
    user = models.OneToOneField(User)
    position = models.CharField(max_length=1, choices=POSITIONS)

    def populate(self, new_username):
        self.user = User.objects.get(username=new_username)
        self.user.save()
        self.save()

    def __unicode__(self):
        return self.user.username
        

class AssetManager(models.Manager):
    # note: by default MySql string comparison is case-insensitive
    def get_search_result(self, searchcat, searchtext):
        if searchcat == 'ti':
            return super(AssetManager, self).get_query_set().filter(title__icontains=searchtext)
        elif searchcat == 'ty':
            return super(AssetManager, self).get_query_set().filter(mime_type__iexact=searchtext)
        elif searchcat == 'us':
            return super(AssetManager, self).get_query_set().filter(uid__user__username__icontains=searchtext)
        elif searchcat == 'ta':
            result = set()
            searchkeywords = Keyword.objects.filter(text__icontains=searchtext)
            for searchkeyword in searchkeywords:
                result.update(searchkeyword.asset_set.all())
            return list(result)
        else:
            return super(AssetManager, self).get_query_set()

    def get_by_user(self, username):
        return super(AssetManager, self).get_query_set().filter(uid__user__username__iexact=username)

    def get_by_month(self, year, month):
        return super(AssetManager, self).get_query_set().filter(updated__year=year).filter(updated__month=month)

    def get_by_exact_title(self, title):
        return super(AssetManager, self).get_query_set().filter(title__exact=title)

class Asset(models.Model):
    objects = AssetManager()

    aid = models.AutoField(primary_key=True)
    uid = models.ForeignKey('DacUser')
    mime_type = models.CharField(max_length=200)
    nice_type = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    submitted = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    keywords = models.ManyToManyField('Keyword')

    def __unicode__(self):
        return self.title

    def str_keywords(self):
        return ', '.join(keyword.text for keyword in self.keywords.all())

    def populate(self, username, info):
        self.title = info['title'] if info['title'] != '' else info['file'].name
        self.mime_type = info['file'].content_type
        # set nice_type to either original file extention or 'unknown'
        ori_type = info['file'].name[info['file'].name.rfind('.')+1:]
        self.nice_type = ori_type if len(ori_type) <= 4 else 'unknown'

        self.uid = DacUser.objects.get(user__username=username)
        self.save()
        # get/set tags
        delim = ',' if ',' in info[
            'tags'] else None  # split by either space or comma
        tags = [tag.strip() for tag in info['tags'].split(delim)]
        for tag in tags:
            keyword = Keyword.objects.filter(text=tag)
            if keyword:
                self.keywords.add(keyword[0])
            else:
                keyword = Keyword()
                keyword.text = tag
                keyword.save()
                self.keywords.add(keyword)

    def str_filename(self):
        # to be given to file to be downloaded
        # <title.replace(' ','_')>.<nice_type>
        ext = ''.join(['.',self.nice_type])
        if (self.nice_type == 'unknown') or (self.title[-len(ext):] == ext):
            ext = ''
        return ''.join([self.title.replace(' ','_'),ext])
    
    def gen_full_file_name(self):
        return '/'.join([self.gen_file_path(), self.gen_file_name()])
    
    def gen_file_name(self):
        return ''.join(['dacf_', str(self.aid)])

    def gen_file_path(self):
        return '/'.join([FILE_DIR, str(self.submitted.year), str(self.submitted.month)])


class Keyword(models.Model):
    kid = models.AutoField(primary_key=True)
    text = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.text
