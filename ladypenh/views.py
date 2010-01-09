# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_control
from ragendja.template import render_to_response
from ragendja.dbutils import get_object
from ladypenh.models import ImageFile, Event, VenueFile
from datetime import datetime, date
from google.appengine.ext import db
import helpers
import mimetypes


## feed pages
def feed_atom(request):
    "Phnom Penh events of the day"
    today = helpers.today()
    return  render_to_response(request, 'ladypenh/atom.xml',
                               dict(events=helpers.get_events([today]),
                                    today=today),
                               mimetype='application/atom+xml; charset=utf8')

def overview(request, dayspan=0):
    days = helpers.get_days(dayspan)
    return  render_to_response(request, 'ladypenh/overview.html',
                               dict(events=helpers.get_events(days)))

def printable_listing(request, dayspan=0):
    days = helpers.get_days(dayspan)
    return  render_to_response(request, 'ladypenh/print.html',
                               dict(events=helpers.get_events(days)))

## "static pages"
def about(request):
    return  render_to_response(request, 'ladypenh/about.html',
                               dict(theme_name=helpers.get_theme(helpers.today())))
def friends(request):
    friends = helpers.get_friends()
    return  render_to_response(request, 'ladypenh/friends.html',
                               dict(friends=friends,
                                    theme_name=helpers.get_theme(helpers.today())))


def archives(request, tag=None):
    return render_to_response(request, 'ladypenh/archives.html',
                              dict(theme_name=helpers.get_theme(helpers.today()),
                                   articles=helpers.get_articles(helpers.today(), tag),
                                   tags=helpers.get_tags()))

def article(request, id):
    article, tags = helpers.get_article_by_id(id)
    return  render_to_response(request, 'ladypenh/article.html',
                               dict(theme_name=helpers.get_theme(helpers.today()),
                                    article=article,
                                    tags=tags))

def event(request, id):
    return  render_to_response(request, 'ladypenh/event.html',
                               dict(theme_name=helpers.get_theme(helpers.today()),
                                    event=helpers.get_event_by_id(id)))

def lpvenue(request, venue):
    days = helpers.get_days()
    venue = helpers.get_venue_by_name(venue)
    return render_to_response(request, 'ladypenh/venue.html',
                              dict(theme_name=helpers.get_theme(helpers.today()),
                                   events=helpers.get_venue_events(days, venue.key()),
                                   files=helpers.get_venue_files(days, venue.key()),
                                   venue=venue))

def venue(request, key):
    days = helpers.get_days()
    key = db.Key(key)
    return render_to_response(request, 'ladypenh/venue.html',
                              dict(theme_name=helpers.get_theme(helpers.today()),
                                   events=helpers.get_venue_events(days, key),
                                   files=helpers.get_venue_files(days, key),
                                   venue=helpers.get_venue_by_key(key)))

def robots(request):
    return HttpResponse("", mimetype="text/plain")

# needed after every reboot in dev env. to allow access to the admin interface
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


def index(request, edito=True):
    offset=0
    if 'offset' in request.GET:
        offset = int(request.GET['offset'])
    days = helpers.get_days(offset)
    daylabels = [(days[0], 'Today'), (days[1], 'Tomorrow')]
    for day in days[2:]:
        daylabels.append((day, day.strftime('%A')))
    daysinfo, highlights = helpers.get_daysinfo_and_highlights(days)
    article, tags = None, []
    if edito:
        article, tags = helpers.get_article(days[0])
    return  render_to_response(request, 'ladypenh/index.html', 
                               dict(article=article,
                                    days=days,
                                    daylabels=daylabels,
                                    daysinfo=daysinfo,
                                    highlights=highlights,
                                    tags=tags,
                                    theme_name=helpers.get_theme(days[0]),
                                    offset=offset,
                                    logged=request.user.is_authenticated()))

def indexlight(request, edito=True):
    offset=0
    if 'offset' in request.GET:
        offset = int(request.GET['offset'])
    days = helpers.get_days(offset)
    daylabels = [(days[0], 'Today'), (days[1], 'Tomorrow')]
    for day in days[2:]:
        daylabels.append((day, day.strftime('%A')))
    daysinfo, highlights = helpers.get_daysinfo_and_highlights(days)
    article, tags = None, []
    if edito:
        article, tags = helpers.get_article(days[0])
    return  render_to_response(request, 'ladypenh/indexlight.html', 
                               dict(article=article,
                                    days=days,
                                    daylabels=daylabels,
                                    daysinfo=daysinfo,
                                    highlights=highlights,
                                    tags=tags,
                                    theme_name=helpers.get_theme(days[0]),
                                    offset=offset,
                                    logged=request.user.is_authenticated()))


def dump_events(request):
    events = Event.gql('WHERE date >= :1', date.today()).fetch(1000)
    import pickle, StringIO
    out = StringIO.StringIO()
    for event in events:
        pickle.dump(event.make_dic(), out, True)
    return HttpResponse(out.getvalue(), 'application/octet-stream')
