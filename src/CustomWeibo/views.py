from django.http import HttpResponse, HttpResponseRedirect  
from django.shortcuts import render_to_response
import datetime
import settings
import util.common as common
from models import Users

def index(request):
	u = common.check_cookie(request)
	if u is None:
		return render_to_response('custom_weibo/signin.html')
	return render_to_response('custom_weibo/index.html', {'user':u})

def signin(request):
	client = common.create_client()
	return HttpResponseRedirect(client.get_authorize_url())

def callback(request):
	code = request.GET['code']
	client = common.create_client()
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
	common.make_cookie(resp, uid, access_token, expires_in)
	return resp