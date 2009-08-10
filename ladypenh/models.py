# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db
from datetime import datetime, date, time, timedelta


class ImageFile(db.Model):
    def __unicode__(self):
        return self.name
    name = db.StringProperty(required=True)
    blob = db.BlobProperty(required=True)

class Venue(db.Model):
    def __unicode__(self):
        return self.name
    name = db.StringProperty(required=True)
    address = db.StringProperty(required=True)
    linktext = db.StringProperty()
    linkurl = db.StringProperty()
    mapurl = db.StringProperty()
    oneshot = db.BooleanProperty(default=False)

class Event(db.Model):
    def __unicode__(self):
        return "%s %s, %s (%s) @ %s" % (str(self.date), str(self.time), self.title, self.type, self.venue.name)
    numid = db.IntegerProperty()
    type = db.StringProperty(required=True, choices=set(['cinema', 'circus', 'concert', 'conference', 'exhibition', 'game', 'party', 'sports', 'live_show', 'videogames', 'visit', 'workshop']))
    venue = db.ReferenceProperty(Venue, required=True)
    organizer = db.StringProperty()
    title = db.StringProperty(required=True)
    date = db.DateProperty(default=date.today, required=True)
    time = db.TimeProperty(default="20:00", required=True)    
    description = db.TextProperty(required=True)
    shortdesc = db.TextProperty(required=True)
    picname = db.StringProperty()
    picheight = db.IntegerProperty()
    picwidth = db.IntegerProperty()
    haslargepic = db.BooleanProperty(default=False)
    highlight = db.BooleanProperty(default=False)
    status = db.StringProperty(default="lp_display", required=True, choices=set(["need_moderation", "lp_nodisplay", "lp_display", "lp_nodate"])) #lp_nodate is for little info popups (not exactly events, right)

class OneLiner(db.Model):
    def __unicode__(self):
        return self.title
    daycode = db.IntegerProperty(default=0, required=True) #1 mon, 135 mon wed fri, -1 everyday but monday, 0 everyday
    daystart = db.DateProperty(default=date.today, required=True)
    dayend = db.DateProperty(default=date.today, required=True)
    title = db.StringProperty(required=True)
    #event = db.ReferenceProperty(Event)

class Article(db.Model):
    def __unicode__(self):
        return self.title
    numid = db.IntegerProperty()
    date = db.DateProperty(default=date.today, required=True)
    title = db.StringProperty(required=True)
    header = db.TextProperty(required=True)
    picname = db.StringProperty(required=True)
    piccredits = db.StringProperty(required=True)
    content = db.TextProperty()
    legacy_comment_url = db.StringProperty() #to deal with older install intense debate comments
    
