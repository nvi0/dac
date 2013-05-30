import mimetypes
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

import helpers
from dac.settings import FILE_DIR
from ldap_getter import get_user_info

POSITIONS = (
    ('f', 'Faculty'),
    ('s', 'Staff'),
    ('u', 'Student'),
)
CATEGORIES = {'ti': 'title', 'ty': 'mime_type', 'us': 'uid', 'ta': 'kid'}
USER_CATEGORIES = {'u': 'username', 'n': 'name', 'r': 'role'}


class DacUserManager(models.Manager):
    # note: by default MySql string comparison is case-insensitive
    def get_search_result(self, searchcat, searchtext):
        if searchtext != '':
            if searchcat == 'u':
                return super(DacUserManager, self).get_query_set().filter(user__username__icontains=searchtext).order_by('position')
            elif searchcat == 'n':
                # TODO: untested cuz no data
                return (super(DacUserManager, self).get_query_set().filter(user__first_name__icontains=searchtext) | super(DacUserManager, self).get_query_set().filter(user__last_name__icontains=searchtext)).order_by('position')
            elif searchcat == 'r':
                searchtext = searchtext.title()
                position_abbr = 'xyz'
                for abbr,p in POSITIONS:
                    if p == searchtext:
                        position_abbr = abbr
                        break
                return super(DacUserManager, self).get_query_set().filter(position=position_abbr).order_by('position')
        #default
        return super(DacUserManager, self).get_query_set()
    
    
        
class DacUser(models.Model):
    objects = DacUserManager()
    
    user = models.OneToOneField(User)
    position = models.CharField(max_length=1, choices=POSITIONS)

    def populate(self, new_username, user_info=None, position=None):
        """
        Populate new user. Default position: Student
        """
        if user_info == None:
            user_info = get_user_info(new_username)
        if not user_info:
            return False
                
        users = User.objects.filter(username=new_username)
        self.user = User.objects.create_user(new_username, user_info['mail'], 'anything') if len(users) == 0 else users[0]
        self.user.first_name = user_info['first_name']
        self.user.last_name = user_info['last_name']
        self.user.save()
        self.position = position if position != None else 'u'
        self.save()
        return True

    def __unicode__(self):
        return self.user.username
        
    def set_position(self, new_p):
        if new_p in [POSITIONS[i][0] for i in range(len(POSITIONS))]:
            self.position = new_p
            self.save()
        else:
            logger.warning('Attempt to set user role to strange value, value= {new_p}'.format(new_p=new_p))
    
    def is_student(self):
        return self.position == 'u'
    
    def is_power(self):
        """
        Rule: either Faculty or Staff
        """
        return self.position == 'f' or self.position == 's'
    
    def f_selected(self):
        return 'selected' if self.position == 'f' else ''
    def s_selected(self):
        return 'selected' if self.position == 's' else ''
    def u_selected(self):
        return 'selected' if self.position == 'u' else ''
    
    def name_positionselect(self):
        return 'ps_{uid}'.format(uid=self.user.id)
        

class AssetManager(models.Manager):
    # note: by default MySql string comparison is case-insensitive
    def get_search_result(self, searchcat, searchtext):
        if searchcat == 'ti':
            return super(AssetManager, self).get_query_set().filter(title__icontains=searchtext)
        elif searchcat == 'ty':
            return super(AssetManager, self).get_query_set().filter(nice_type__icontains=searchtext) #was mime_type__iexacts
        elif searchcat == 'us':
            return super(AssetManager, self).get_query_set().filter(uid__user__username__icontains=searchtext)
        elif searchcat == 'ta':
            return super(AssetManager, self).get_query_set().filter(keywords__text__icontains=searchtext)
        else:
            return super(AssetManager, self).get_query_set()
            
    def get_search_result2(self, searchtext, searchtype, searchowner, searchtag):
        return super(AssetManager, self).get_query_set().filter(title__icontains=searchtext, nice_type__icontains=searchtype, uid__user__username__icontains=searchowner, keywords__text__icontains=searchtag).distinct()

    def get_by_user(self, username):
        return super(AssetManager, self).get_query_set().filter(uid__user__username__iexact=username)

    def get_by_month(self, year, month):
        return super(AssetManager, self).get_query_set().filter(updated__year=year).filter(updated__month=month)

    def get_by_exact_title(self, title):
        return super(AssetManager, self).get_query_set().filter(title__exact=title)

    def get_predefined_search_list(self):
        return {'type_list':super(AssetManager, self).get_query_set().values_list('nice_type', flat=True).order_by('nice_type').distinct(),
                'owner_list':super(AssetManager, self).get_query_set().values_list('uid__user__username', flat=True).order_by('uid__user__username').distinct(),
                'tag_list':super(AssetManager, self).get_query_set().values_list('keywords__text', flat=True).order_by('keywords__text').distinct()}
    
    
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
        tags = self.set_keywords(info['tags'])
        #helpers.update_predefined_search_list([self.nice_type], [username], tags)
    
    def populate_overwrite(self, new_mime_type, new_nice_type, new_keywords):
        self.mime_type = new_mime_type
        self.nice_type = new_nice_type
        self.save()
        tags = self.set_keywords(new_keywords)
        #helpers.update_predefined_search_list([new_nice_type], [self.uid.user.username], tags)

    
    def set_keywords(self, new_keywords):
        # remove any old keywords
        self.keywords.clear()
        
        # set new keywords
        delim = ',' if ',' in new_keywords else None  # split by either space or comma
        tags = [tag.strip() for tag in new_keywords.split(delim)]
        for tag in tags:
            keyword = Keyword.objects.filter(text=tag)
            if keyword:
                self.keywords.add(keyword[0])
            else:
                # create new entry in table keyword
                self.keywords.create(text=tag)
        return tags

    def set_title(self, new_title):
        if self.title == new_title:
            return True
        if not Asset.objects.get_by_exact_title(new_title):
            self.title = new_title
            self.save()
            return True
        return False

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
    
    def get_edit_tag_id(self):
        # et_<aid>
        return '_'.join(['et',str(self.aid)]) 

    def get_edit_title_id(self):
        # etitle_<aid>
        return '_'.join(['etitle',str(self.aid)])
    


class Keyword(models.Model):
    kid = models.AutoField(primary_key=True)
    text = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.text
