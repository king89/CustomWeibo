from weibo import  APIClient
from CustomWeibo.settings import *
import base64
import hashlib
import time
from CustomWeibo.models import Users

_COOKIE = 'authuser'
_SALT = '12345'

def create_client():
    return APIClient(APP_ID, APP_SECRET, APP_CALLBACK_URL)

def make_cookie(response, uid, token, expires_in):
    expires = str(int(expires_in))
    s = '%s:%s:%s:%s' % (str(uid), str(token), expires, _SALT)
    md5 = hashlib.md5(s).hexdigest()
    cookie = '%s:%s:%s' % (str(uid), expires, md5)
    response.set_cookie(_COOKIE, base64.b64encode(cookie).replace('=', '_'), expires=expires_in)

def check_cookie(request):
    try:
        b64cookie = request.COOKIES[_COOKIE]
        cookie = base64.b64decode(b64cookie.replace('_', '='))
        uid, expires, md5 = cookie.split(':', 2)
        if int(expires) < time.time():
            return
        L = Users.objects.filter(id=uid)
        if not L:
            return
        u = L[0]
        s = '%s:%s:%s:%s' % (uid, str(u.auth_token), expires, _SALT)
        if md5 != hashlib.md5(s).hexdigest():
            return
        return u
    except BaseException:
        pass