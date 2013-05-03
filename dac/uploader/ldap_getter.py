import ldap
from dac.settings import LDAP_URL, LDAP_BASE_DN

def get_user_info(username):
    ld = ldap.initialize(LDAP_URL)
    ld.simple_bind_s()
    results = ld.search_s(LDAP_BASE_DN, ldap.SCOPE_SUBTREE, 'uid={u}'.format(u=username))
    l = len(results)
    if l < 1:
        return None
    elif l > 1:
        logger.warning('Found {l} matches for username= {u}'.format(l=l, u=username))
    
    r = results[0][1]
    m = {'mail': r.get('mail',[''])[0],
         'first_name': r.get('givenName',[''])[0],
         'last_name': r.get('sn',[''])[0],
         }
    return m