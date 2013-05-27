# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ladypenh.views',

    #(r'^initfuckingadminondevenv$', 'create_admin_user'),

#feeds
    (r'^feed/atom$', 'feed_atom'),
#legacy feed addresses
    (r'^atom$', 'feed_atom'),    
    (r'^atom.xml$', 'feed_atom'),    

    (r'^flush_cache$', 'flush_cache'),
    (r'^robots.txt$', 'robots'),
    (r'^file/(?P<filename>.+)$', 'file'),
    (r'^image/(?P<name>.+)$', 'image'),
    (r'^about.html$', 'about'),
    (r'^friends.html$', 'friends'),
    (r'^archives.html$', 'archives'),
    (r'^archives/(?P<tag>.+).html$', 'archives'),
    (r'^article(?P<nid>\d+).html$', 'article'),
    (r'^print.html$', 'printable_listing'),
    (r'^events/(?P<date>.+).html$', 'events'),
    (r'^venue/(?P<key>[\w-]+).html$', 'venue'),                       
    (r'^index.html$', 'events'),
    (r'^(?P<venue>\w+).html$', 'lpvenue'),    
    (r'^None$', 'events'),
    (r'^$', 'events'),
)
