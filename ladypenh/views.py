# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_control
from ragendja.template import render_to_response
from ragendja.dbutils import get_object
from ladypenh.models import ImageFile, Event, VenueFile
from datetime import datetime, date
from google.appengine.ext import db
from google.appengine.api import memcache
import helpers
import mimetypes


## feed pages
@helpers.use_cache
def feed_atom(request):
    "Phnom Penh events of the day"
    today = helpers.today()
    return  render_to_response(request, 'ladypenh/atom.xml',
                               dict(events=helpers.get_events(today),
                                    today=today),
                               mimetype='application/atom+xml; charset=utf8')


@helpers.use_cache
def printable_listing(request, dayspan=0):
    days = helpers.get_days(dayspan)
    return  render_to_response(request, 'ladypenh/print.html',
                               dict(events=helpers.get_events(days)))

## "static pages"
@helpers.use_cache
def about(request):
    return  render_to_response(request, 'ladypenh/about.html',
                               dict(theme_name=helpers.get_theme(helpers.today())))

@helpers.use_cache
def friends(request):
    friends = helpers.get_friends()
    return  render_to_response(request, 'ladypenh/friends.html',
                               dict(friends=friends,
                                    theme_name=helpers.get_theme(helpers.today())))

@helpers.use_cache
def events(request, date=None):
    today = day = datetime.now().date()
    try:
        reqday = datetime.strptime(date, "%Y-%m-%d").date()
        if request.user.is_authenticated() or (reqday - day).days in range(7):
            day = reqday
    except:
        # just use today date
        pass
    days = helpers.get_days(0)
    daylabels = [(days[0], 'Today'), (days[1], 'Tomorrow')]
    for d in days[2:]:
        daylabels.append((d, d.strftime('%A')))
    article, tags = None, []
    show_edit_links = False
    if request.user.is_authenticated():
        show_edit_links = True
    article,tags=helpers.get_article(today)
    return  render_to_response(request, 'ladypenh/day.html',
                               dict(theme_name=helpers.get_theme(helpers.today()),
                                    day=day,                               
                                    daylabels=daylabels,
                                    highlights=helpers.get_highlights(days),
                                    events=helpers.get_events(day),
                                    reminders=helpers.get_reminders(day),
                                    show_edit_links=show_edit_links,
                                    article=article,
                                    tags=tags
                                    ))

@helpers.use_cache
def lpvenue(request, venue):
    days = helpers.get_days()
    venue = helpers.get_venue_by_name(venue)
    return render_to_response(request, 'ladypenh/venue.html',
                              dict(theme_name=helpers.get_theme(helpers.today()),
                                   events=helpers.get_venue_events(days, venue.key()),
                                   files=helpers.get_venue_files(days, venue.key()),
                                   venue=venue))

@helpers.use_cache
def venue(request, key):
    days = helpers.get_days()
    key = db.Key(key)
    return render_to_response(request, 'ladypenh/venue.html',
                              dict(theme_name=helpers.get_theme(helpers.today()),
                                   events=helpers.get_venue_events(days, key),
                                   files=helpers.get_venue_files(days, key),
                                   venue=helpers.get_venue_by_key(key)))

@helpers.use_cache
def robots(request):
    return HttpResponse("", mimetype="text/plain")

# needed after every reboot in dev env. to allow access to the admin interface
@helpers.use_cache
def create_admin_user(request):
    from django.contrib.auth.models import User
    user = User.get_by_key_name('admin')
    if not user or user.username != 'admin' or not (user.is_active and
            user.is_staff and user.is_superuser and
            user.check_password('admin')):
        user = User(key_name='admin', username='admin',
            email='admin@localhost', first_name='Boss', last_name='Admin',
            is_active=True, is_staff=True, is_superuser=True)
        user.set_password('admin')
        user.put()
    return HttpResponseRedirect('/')


#treat blobfiles as immutable
defaultdate = datetime(year=1998, month=6, day=22)

@cache_control(public=True, max_age=3600*24*60*60)
def image(request, name):
    mime = mimetypes.guess_type(name)[0]
    bfiles = ImageFile.gql("WHERE name = :1", name).fetch(1)
    response = HttpResponse(bfiles[0].blob, mimetype=mime)
    response['Last-Modified'] = defaultdate.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return response    


@cache_control(public=True, max_age=3600*24*60*60)
def file(request, filename):
    mime = mimetypes.guess_type(filename)[0]
    file = VenueFile.gql("WHERE filename = :1", filename).fetch(1)
    response = HttpResponse(file[0].blob, mimetype=mime)
    response['Last-Modified'] = defaultdate.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return response    


def flush_cache(request):
    return HttpResponse(memcache.flush_all(), mimetype="text/plain")    


@helpers.use_cache
def archives(request, tag=None):
    return render_to_response(request, 'ladypenh/archives.html',
                              dict(theme_name=helpers.get_theme(helpers.today()),
                                   articles=helpers.get_articles(helpers.today(), tag),
                                   tags=helpers.get_tags()))

@helpers.use_cache
def article(request, nid):
    article, tags = helpers.get_article_by_id(nid)
    return  render_to_response(request, 'ladypenh/article.html',
                               dict(theme_name=helpers.get_theme(helpers.today()),
                                    article=article,
                                    tags=tags))
