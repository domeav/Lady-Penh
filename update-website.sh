#!/bin/bash
date && mkdir -p /home/dom/perso/ladypenh/cache && cd /home/dom/perso/ladypenh/cache && /usr/bin/wget --mirror -N -nH http://ladypenh.appspot.com/index.html http://ladypenh.appspot.com/ijustwanttheprogramthanks.html http://ladypenh.appspot.com/feed/tomorrow_overview.html && rsync -rvu . ladypenh@ladypenh.com:www/
