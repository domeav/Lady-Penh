#!/bin/bash
date && mkdir -p /home/dom/perso/ladypenh/django-appengine/cache && cd /home/dom/perso/ladypenh/django-appengine/cache && /usr/bin/wget --mirror -N -nH http://ladypenh.appspot.com/index.html http://ladypenh.appspot.com/ijustwanttheprogramthanks.html http://ladypenh.appspot.com/feed/tomorrow_overview.html && rsync -rvu . ladypenh@ladypenh.com:www/
