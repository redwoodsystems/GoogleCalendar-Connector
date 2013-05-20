from django.conf.urls import patterns, include, url

from django.conf.urls.defaults import patterns, url

from djangorestframework.mixins import ListModelMixin, CreateModelMixin
from djangorestframework.views import View, ModelView

from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from reaper.models import RoomConfig, RoomStatus, ReaperLog, PseudoRoomMotion, PseudoRoomResv

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

class RoomConfigResource(ModelResource):
    model = RoomConfig

class RoomStatusResource(ModelResource):
    model = RoomStatus

class ReaperLogResource(ModelResource):
    model = ReaperLog

class PseudoRoomMotionResource(ModelResource):
    model = PseudoRoomMotion

class PseudoRoomResvResource(ModelResource):
    model = PseudoRoomResv
    
    
class RMStatusView(ListModelMixin, CreateModelMixin, ModelView):

    def initial(self, request, *args, **kargs):
        print "In RMStatusView ..initial..."
        print (request.GET)
        
        if 'jsonpCallback' in request.GET or 'callback' in request.GET:
            #hack around jquery's inability to set accept headers on cross origin json requests
            #django rest framework needs a specific Accept: parameter to render jsonp
            #print "request is probably a JSONP request"
            #print request.META
            request.META['HTTP_ACCEPT'] = 'application/json-p'
    
    """
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(View, cls).as_view(**initkwargs)
        view.cls_instance = cls(**initkwargs)
        return view
    """

class RoomConfigView(ListModelMixin, CreateModelMixin, ModelView):

    def initial(self, request, *args, **kargs):
        print "In RoomConfigView ..initial..."
        print (request.GET)
        
        if 'jsonpCallback' in request.GET or 'callback' in request.GET:
            #hack around jquery's inability to set accept headers on cross origin json requests
            #django rest framework needs a specific Accept: parameter to render jsonp
            #print "request is probably a JSONP request"
            #print request.META
            request.META['HTTP_ACCEPT'] = 'application/json-p'

class ReaperLogView(ListModelMixin, CreateModelMixin, ModelView):

    def initial(self, request, *args, **kargs):
        print "In ReaperLogView ..initial..."
        print (request.GET)
        
        if 'jsonpCallback' in request.GET or 'callback' in request.GET:
            #hack around jquery's inability to set accept headers on cross origin json requests
            #django rest framework needs a specific Accept: parameter to render jsonp
            #print "request is probably a JSONP request"
            #print request.META
            request.META['HTTP_ACCEPT'] = 'application/json-p'


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^api/rmconfig$', RoomConfigView.as_view(resource=RoomConfigResource)),
    url(r'^api/rmconfig/(?P<pk>[^/]+)/$', InstanceModelView.as_view(resource=RoomConfigResource)),
    
    #url(r'^api/rmstatus$', ListOrCreateModelView.as_view(resource=RoomStatusResource)),
    url(r'^api/rmstatus$', RMStatusView.as_view(resource=RoomStatusResource)),    
    url(r'^api/rmstatus/(?P<pk>[^/]+)/$', InstanceModelView.as_view(resource=RoomStatusResource)),
    
    url(r'^api/reaperlog$', ReaperLogView.as_view(resource=ReaperLogResource)),
    url(r'^api/reaperlog$/(?P<pk>[^/]+)/$', InstanceModelView.as_view(resource=ReaperLogResource)),
    
)
