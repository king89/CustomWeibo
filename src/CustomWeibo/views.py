# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect  
from django.shortcuts import render_to_response
from datetime import datetime, tzinfo, timedelta
import time
import settings
from util.weibo import  APIError
from util.common import jsonresult,check_cookie,make_cookie,create_client,_COOKIE
from models import Users


_TD_ZERO = timedelta(0)
_TD_8 = timedelta(hours=8)

class UTC8(tzinfo):
    def utcoffset(self, dt):
        return _TD_8

    def tzname(self, dt):
        return "UTC+8:00"

    def dst(self, dt):
        return _TD_ZERO

_UTC8 = UTC8()

def _format_datetime(dt):
    t = datetime.strptime(dt, '%a %b %d %H:%M:%S +0800 %Y').replace(tzinfo=_UTC8)
    return time.mktime(t.timetuple())

def _format_user(u):
    return dict(id=str(u.id), screen_name=u.screen_name, profile_url=u.profile_url, verified=u.verified, verified_type=u.verified_type, profile_image_url=u.profile_image_url)

def _format_weibo(st):
    r = dict(
        user = _format_user(st.user),
        text = st.text,
        created_at = _format_datetime(st.created_at),
        reposts_count = st.reposts_count,
        comments_count = st.comments_count,
    )
    if 'original_pic' in st:
        r['original_pic'] = st.original_pic
    if 'thumbnail_pic' in st:
        r['thumbnail_pic'] = st.thumbnail_pic
    if 'retweeted_status' in st:
        r['retweeted_status'] = _format_weibo(st.retweeted_status)
    return r

def requires_login(view):
    def new_view(request, *args, **kwargs):
        u = check_cookie(request)
        if not u:
            return render_to_response('custom_weibo/signin.html')
        kwargs['user'] = u
        return view(request, *args, **kwargs)
    return new_view


@requires_login
def index(request, user=None):
    return render_to_response('custom_weibo/index.html', {'user':user})

def signin(request):
    client = create_client()
    return HttpResponseRedirect(client.get_authorize_url())

def signout(request):
    resp = HttpResponseRedirect('/')
    resp.delete_cookie(_COOKIE)
    return resp

def callback(request):
    code = request.GET['code']
    client = create_client()
    r = client.request_access_token(code)
    access_token, expires_in, uid = r.access_token, r.expires_in, r.uid
    client.set_access_token(access_token, expires_in)
    u = client.users.show.get(uid=uid)
    
    users = Users.objects.filter(id=uid)
    user = dict(name=u.screen_name, \
            image_url=u.avatar_large or u.profile_image_url, \
            statuses_count=u.statuses_count, \
            friends_count=u.friends_count, \
            followers_count=u.followers_count, \
            verified=u.verified, \
            verified_type=u.verified_type, \
            auth_token=access_token, \
            expired_time=expires_in)
    if users:
        pass
    else:
        user['id'] = uid
        Users.objects.create(**user)
    resp = HttpResponseRedirect(r"/")
    make_cookie(resp, uid, access_token, expires_in)
    return resp


@requires_login
@jsonresult
def friends(request,user=None):
    u = user
    client = create_client()
    client.set_access_token(u.auth_token, u.expired_time)
    try:
        r = client.friendships.friends.get(uid=u.id, count=99)
        return [_format_user(u) for u in r.users]
    except APIError, e:
        return dict(error='failed')


@requires_login
@jsonresult  
def load(request,user=None):
    client = create_client()
    client.set_access_token(user.auth_token, user.expired_time)
    try:
        r = client.statuses.home_timeline.get()
        return [_format_weibo(s) for s in r.statuses]
    except APIError, e:
        return dict(error='failed')


