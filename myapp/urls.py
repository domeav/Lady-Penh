# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('myapp.views',
    (r'^create_admin_userXXX$', 'create_admin_user'), #to remove, of course
    (r'^$', 'list_people'),
    (r'^create/$', 'add_person'),
    (r'^show/(?P<key>.+)$', 'show_person'),
    (r'^edit/(?P<key>.+)$', 'edit_person'),
    (r'^delete/(?P<key>.+)$', 'delete_person'),
    (r'^download/(?P<key>.+)/(?P<name>.+)$', 'download_file'),
)
