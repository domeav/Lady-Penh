# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ladypenh.views',
    #(r'^initfuckingadminondevenv$', 'create_admin_user'),
    (r'^dump_events$', 'dump_events'),
#feeds
    (r'^feed/atom$', 'feed_atom'),
    (r'^feed/overview.html$', 'overview'),
    (r'^feed/tomorrow_overview.html$', 'overview', {'dayspan': 1}),
#legacy feed addresses
    (r'^atom$', 'feed_atom'),    
    (r'^atom.xml$', 'feed_atom'),    
    (r'^overview.html$', 'overview'),
    (r'^tomorrow_overview.html$', 'overview', {'dayspan': 1}),

    (r'^robots.txt$', 'robots'),
    (r'^image/(?P<name>.+)$', 'image'),
    (r'^about.html$', 'about'),
    (r'^friends.html$', 'friends'),
    (r'^archives.html$', 'archives'),
    (r'^archives/(?P<tag>.+).html$', 'archives'),
    (r'^print.html$', 'printable_listing'),
    (r'^article(?P<id>\d+).html$', 'article'),
    (r'^event/(?P<id>\d+).html$', 'event'),
    (r'^ijustwanttheprogramthanks.html$', 'index', {'edito': False}),
    (r'^index.html$', 'index'),
    (r'^$', 'index'),
)
