# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_control
from ragendja.template import render_to_response
from ladypenh.models import ImageFile
import helpers

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
    return  render_to_response(request, 'ladypenh/friends.html',
                               dict(theme_name=helpers.get_theme(helpers.today())))


def archives(request):
    return render_to_response(request, 'ladypenh/archives.html',
                              dict(theme_name=helpers.get_theme(helpers.today()),
                                   articles=helpers.get_articles(helpers.today())))

def article(request, id):
    return  render_to_response(request, 'ladypenh/article.html',
                               dict(theme_name=helpers.get_theme(helpers.today()),
                                    article=helpers.get_article_by_id(id)))

def event(request, id):
    return  render_to_response(request, 'ladypenh/event.html',
                               dict(theme_name=helpers.get_theme(helpers.today()),
                                    event=helpers.get_event_by_id(id)))


# needed every time in dev env. to allow access to the admin interface
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


mime_extensions = {'jpg': 'image/jpeg',
                   'png': 'image/png',
                   'gif': 'image/gif'}

@cache_control(public=True, max_age=3600*24*60*60)
def image(request, name):
    mime = mime_extensions[name.split('.')[-1].lower()]
    images = ImageFile.gql("WHERE name = :1", name).fetch(1)
    if len(images) == 0:
        if name != "notfound.png":
            return HttpResponseRedirect('/image/notfound.png')
        return HttpResponse("Image not found.", mimetype="text/html")
    return HttpResponse(images[0].blob, mimetype=mime)
    

def index(request, edito=True):
    days = helpers.get_days()
    daylabels = [(days[0], 'Today'), (days[1], 'Tomorrow')]
    for day in days[2:]:
        daylabels.append((day, day.strftime('%A')))
    daysinfo, highlights = helpers.get_daysinfo_and_highlights(days)
    article = None
    if edito:
        article = helpers.get_article(days[0])
    return  render_to_response(request, 'ladypenh/index.html', 
                               dict(article=article,
                                    days=days,
                                    daylabels=daylabels,
                                    daysinfo=daysinfo,
                                    highlights=highlights,
                                    theme_name=helpers.get_theme(days[0])))

