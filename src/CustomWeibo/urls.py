from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('CustomWeibo.views',
    # Examples:
    # url(r'^$', 'CustomWeibo.views.home', name='home'),
    # url(r'^CustomWeibo/', include('CustomWeibo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'index', name='home'),
    url(r'^callback/$','callback'),
    url(r'^signin/$','signin'),
    url(r'^load/$','load'),
    url(r'^friends/$','friends'),
    url(r'^signout/$','signout'),
)