from django.conf.urls import patterns, include, url
from gadget.views import render_gadget, render_test_html, render_test_html_new, render_connect_confirmation

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^$', render_gadget),
    url(r'^test$', render_test_html),
    url(r'^test3$', render_test_html_new),
    url(r'^confirm$', render_connect_confirmation),
    
)
