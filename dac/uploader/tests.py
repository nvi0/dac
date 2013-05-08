import urllib2, urllib

from django.test.client import Client
from django.test import TestCase

from dac.uploader.models import *

LABRAT = {'username': '', 'password':''} # any pdx account to pass CAS authentication

class ModelsTest(TestCase):
    def setUp(self):
        user1 = DacUser()
        user1.user = User.objects.create_user('f1', 'f1@abc.com', '1234')
        user1.position = 'f'
        user1.save()
        user2 = DacUser()
        user2.user = User.objects.create_user('f2', 'f2@abc.com', '1234')
        user2.position = 'f'
        user2.save()
        asset1 = Asset()
        asset1.uid = user1
        asset1.title = 'asset1'
        asset1.nice_type = 'txt'
        asset1.save()
        asset2 = Asset()
        asset2.uid = user1
        asset2.title = 'asset2'
        asset2.nice_type = 'pdf'
        asset2.save()
        asset3 = Asset()
        asset3.uid = user2
        asset3.title = 'asset3'
        asset3.nice_type = 'png'
        asset3.save()
        kw1 = Keyword()
        kw1.text = 'tag1'
        kw1.save()
        asset2.keywords.add(kw1)
        kw2 = Keyword()
        kw2.text = 'tag2'
        kw2.save()
        asset2.keywords.add(kw2)
        asset3.keywords.add(kw2)
        # user1: asset1, asset2
        # user2: asset3
        # asset1: no kw
        # asset2: kw1, kw2
        # asset3: kw2
        
        
    def test_stored_data(self):
        self.assertEqual(DacUser.objects.filter(user__username='f1')[0].user.email,'f1@abc.com')
        self.assertEqual(Asset.objects.get_by_user('f2')[0].uid.user.email,'f2@abc.com')
        self.assertEqual(Asset.objects.get_by_user('f1').filter(title='asset2')[0].keywords.filter(text='tag2')[0].text,'tag2')
        self.assertTrue('tag2' in Asset.objects.get_search_result('ti','3')[0].str_keywords())
        self.assertQuerysetEqual(Asset.objects.filter(title__icontains='asset'),['<Asset: asset1>','<Asset: asset2>','<Asset: asset3>'],ordered=False)
        self.assertEqual(Asset.objects.get(title__icontains='3').str_filename(),'asset3.png')
    
    def test_delete(self):
        #user1 = DacUser.objects.get(pk=1)
        #user1.delete()
        asset2 = Asset.objects.get(pk=2)
        asset2.delete()
        self.assertQuerysetEqual(Asset.objects.all(),['<Asset: asset1>','<Asset: asset3>'],ordered=False)
        self.assertQuerysetEqual(Asset.objects.get_by_user('f1'),['<Asset: asset1>'])
        self.assertFalse(Keyword.objects.get(pk=1).asset_set.all())

class ViewsTest(TestCase):
    """
        django.test.client to test inner urls, views matching and templates rendering.
        urllib2 to log in at CAS server.
    """
    def test_all(self):
        client = Client()
        self.assertEqual(client.get('/').status_code, 302)
        self.assertEqual(client.get('/dac/').status_code, 302)
        self.assertEqual(client.get('/dac/login/').status_code, 200) # intro page that contains link to login
        
        r = client.get('/login/')
        self.assertEqual(r.status_code, 302)
        try:
            cas_login_url = r._headers['location'][1]
        except KeyError:
            self.fail()
            
        if LABRAT.get('username','') == '':
            print('No pdx account provided for testing. Halting ViewsTest.')
            return
        
        # cas_login_page = urllib2.urlopen(cas_login_url).read()
        login_req = urllib2.Request(cas_login_url)
        d = LABRAT
        login_req.add_data(urllib.urlencode(d))
        