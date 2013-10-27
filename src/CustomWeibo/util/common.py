# -*- coding: utf-8 -*-
from weibo import  APIClient
from CustomWeibo.settings import *
import base64
import hashlib
import time
import functools
from CustomWeibo.models import Users
from django.http import HttpResponse
import json



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


def _json_dumps(obj):
    '''
    Dumps any object as json string.

    >>> class Person(object):
    ...     def __init__(self, name):
    ...         self.name = name
    >>> _json_dumps([Person('Bob'), None])
    '[{"name": "Bob"}, null]'
    '''
    def _dump_obj(obj):
        if isinstance(obj, dict):
            return obj
        d = dict()
        for k in dir(obj):
            if not k.startswith('_'):
                d[k] = getattr(obj, k)
        return d
    return json.dumps(obj, default=_dump_obj)

def jsonresult(func):
    '''
    Autoconvert result to json str.

    >>> @jsonresult
    ... def hello(name):
    ...     return dict(name=name)
    >>> ctx.response = Response()
    >>> hello('Bob')
    '{"name": "Bob"}'
    >>> ctx.response.header('CONTENT-TYPE')
    'application/json; charset=utf-8'
    >>> hello(None)
    '{"name": null}'
    '''
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        r = func(*args, **kw)
        return HttpResponse(_json_dumps(r))
    return _wrapper

