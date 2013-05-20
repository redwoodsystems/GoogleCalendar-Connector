from django.conf.urls import patterns, include, url

from django.conf.urls.defaults import patterns, url
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from polls.models import Poll
#from reaper import urls as reaper_urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

class MyResource(ModelResource):
    model = Poll

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^polls/$', 'polls.views.index'),
    url(r'^polls/(?P<poll_id>\d+)/$', 'polls.views.detail'),
    url(r'^polls/(?P<poll_id>\d+)/results/$', 'polls.views.results'),
    url(r'^polls/(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
    url(r'^api$', ListOrCreateModelView.as_view(resource=MyResource)),
    url(r'^api/(?P<pk>[^/]+)/$', InstanceModelView.as_view(resource=MyResource)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reaper/', include('reaper.urls')),
    url(r'^gadget/', include('gadget.urls')),
    (r'^admins/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/Vivek/tp/RedwoodSystems/Calendar/rwcal/rwreaper/mysite/templates/admin/static', 'show_indexes': True}),
)


