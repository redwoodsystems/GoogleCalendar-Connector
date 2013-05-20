# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from django.template.response import TemplateResponse

import mysite.settings
import sys

from reaper.models import RoomConfig, RoomStatus



def render_gadget(request):
    
    if request.method == "GET":
        """
        Get rooms from room config
        Paint location boxes
        """
        
        rooms = RoomConfig.objects.filter(motion_enabled=True).order_by('name')
        
        #total_cnt = len(rooms)
        #print total_cnt   
        
        #return render_to_response('gadget/test1.html', {'t_rooms':rooms,})
        #return render_to_response('gadget/reaper.xml', {'t_rooms':rooms,})
        return TemplateResponse(request, 'gadget/reaper2.xml', 
                                         {"t_rm_status_api_url":mysite.settings.GG_RM_STATUS_API_URL,
                                           "t_static_host_url": mysite.settings.GG_STATIC_HOST_URL,
                                           "t_reload_every":mysite.settings.GG_RELOAD_EVERY },
                                         content_type="application/xml")
    
    else:
        return
    
def render_test_html(request):
    
    if request.method == "GET":
        """
        Get rooms from room config
        Paint location boxes
        """
        
        rooms = RoomConfig.objects.filter(motion_enabled=True).order_by('name')
        
        total_cnt = len(rooms)
        print total_cnt   
        
        return render_to_response('gadget/test1.html', {'t_rooms':rooms,})
    
    else:
        return
        
def render_test_html_new(request):
    
    if request.method == "GET":
        """
        Get rooms from room config
        Paint location boxes
        """
        
        rooms = RoomConfig.objects.filter(motion_enabled=True).order_by('name')
        
        return render_to_response('gadget/test3.html', {"t_rm_status_api_url":mysite.settings.GG_RM_STATUS_API_URL,
                                                        "t_static_host_url": mysite.settings.GG_STATIC_HOST_URL,
                                                        "t_reload_every":mysite.settings.GG_RELOAD_EVERY })
    
    else:
        return
    
    
def render_connect_confirmation(request):
    
    if request.method == "GET":
        return render_to_response('gadget/conf.html')
    else:
        return




