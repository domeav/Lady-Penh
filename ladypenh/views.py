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
                               dict(events=helpers.get_events([today]),
                                    today=today),
                               mimetype='application/atom+xml; charset=utf8')

@helpers.use_cache
def overview(request, dayspan=0):
    days = helpers.get_days(dayspan)
    return  render_to_response(request, 'ladypenh/overview.html',
                               dict(events=helpers.get_events(days)))

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

@helpers.use_cache
def event(request, nid):
    return  render_to_response(request, 'ladypenh/event.html',
                               dict(theme_name=helpers.get_theme(helpers.today()),
                                    event=helpers.get_event_by_id(nid)))

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
def venues(request):
    return render_to_response(request, 'ladypenh/venues.html',
                              dict(theme_name=helpers.get_theme(helpers.today()),
                                   venues=helpers.get_venues()))

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


@helpers.use_cache
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


def flush_cache(request):
    return HttpResponse(memcache.flush_all(), mimetype="text/plain")    

def dump_events(request):
    events = Event.gql('WHERE date >= :1', date.today()).fetch(1000)
    import pickle, StringIO
    out = StringIO.StringIO()
    for event in events:
        pickle.dump(event.make_dic(), out, True)
    return HttpResponse(out.getvalue(), 'application/octet-stream')


def btkrawma(request):
    offset=0
    stripgigs = False
    if 'stripgigs' in request.GET:
        stripgigs = True
    if 'offset' in request.GET:
        offset = int(request.GET['offset'])
    days = helpers.get_days(offset, 14)
    events = helpers.get_events(days)

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=BTKrawma.pdf'

    from reportlab.platypus import BaseDocTemplate, PageTemplate, Paragraph, Frame
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from google.appengine.api import images
    from xml.sax.saxutils import escape as esc
    from StringIO import StringIO
    
    w,h = 180*mm, 130*mm

    frames=[]
    frames.append(Frame(20*mm,15*mm,75*mm,110*mm))
    frames.append(Frame(100*mm,15*mm,75*mm,110*mm))

    class JpegBlobImageReader(ImageReader):
        def __init__(self, blob):
            self.fileName = "JPEGBLOB_%d" % id(self)
            self.fp = StringIO()
            self.fp.write(blob)
            self._image = blob
            self.jpeg_fh = self._jpeg_fh
            self._data = blob
            self._dataA = None
            image = images.Image(blob)
            self._width = image.width
            self._height = image.height
            self._transparent = False 

    def graphics(canvas, document):
        bfiles = ImageFile.gql("WHERE name = :1", "BTPdfbackground.jpg").fetch(1)
        img = JpegBlobImageReader(bfiles[0].blob)
        canvas.drawImage(img, 5*mm, 3*mm, width=168*0.95*mm, height=121*0.95*mm)
        pass

    doc = BaseDocTemplate(response)              
    doc.showBoundary=False
    doc.addPageTemplates([PageTemplate(id='Schedule',
                                       frames=frames,
                                       pagesize=(w,h),
                                       onPage=graphics)])



    style = getSampleStyleSheet()['Normal']
    style.fontsize = 10
    style.spaceAfter = 5
    style.fontName = 'Helvetica'
    elements=[]

    currentday = None
    dayschedule = StringIO()    
    for event in events:
        if stripgigs and event.type == 'concert':
            continue
        if event.date != currentday:
            if currentday != None:
                elements.append(Paragraph(dayschedule.getvalue(),style))
                dayschedule = StringIO()
            dayschedule.write('<font color="darkblue" size="11"><b>')
            dayschedule.write(event.date.strftime('%a %b %d: '))
            dayschedule.write('</b></font>')
            currentday = event.date
        dayschedule.write('<b>%s</b> %s @ %s ' % (event.time.strftime('%H:%M'), 
                                               esc(event.title), 
                                               esc(event.venue.name)))
    elements.append(Paragraph(dayschedule.getvalue(),style))        

    doc.build(elements)
    return response
