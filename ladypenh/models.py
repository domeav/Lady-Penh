# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db
from datetime import datetime, date, time, timedelta
from ragendja.dbutils import KeyListProperty


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
    details = db.TextProperty()
    ladypenh_url = db.StringProperty()


class VenueFile(db.Model):
    def __unicode__(self):
        return self.name
    name = db.StringProperty(required=True)
    filename = db.StringProperty()
    blob = db.BlobProperty(required=True)
    venue = db.ReferenceProperty(Venue, required=True)
    valid_until = db.DateProperty()
    
    

class Event(db.Model):
    def __unicode__(self):
        return "%s %s, %s (%s) @ %s" % (str(self.date), str(self.time), self.title, self.type, self.venue.name)
    def make_dic(self):
        dump = {}
        for att in ['numid', 'type', 'venue', 'organizer', 'title', 'date', 'time', 'description',
                    'shortdesc', 'picname', 'highlight', 'status']:
            dump[att] = unicode(getattr(self, att))
        return dump
    numid = db.IntegerProperty()
    type = db.StringProperty(required=True, choices=set(['cinema', 'circus', 'concert', 'conference', 'exhibition', 'game', 'party', 'rock', 'sports', 'live_show', 'videogames', 'visit', 'workshop']))
    venue = db.ReferenceProperty(Venue, required=True)
    organizer = db.StringProperty()
    title = db.StringProperty(required=True)
    date = db.DateProperty(default=date.today, required=True)
    time = db.TimeProperty(default="20:00", required=True)
    until = db.StringProperty()
    description = db.TextProperty(required=True)
    shortdesc = db.TextProperty(required=True)
    picname = db.StringProperty()
    picheight = db.IntegerProperty()
    picwidth = db.IntegerProperty()
    haslargepic = db.BooleanProperty(default=False)
    highlight = db.BooleanProperty(default=False)
    status = db.StringProperty(default="lp_display", required=True, choices=set(["need_moderation", "lp_nodisplay", "lp_display"]))

class OneLiner(db.Model):
    def __unicode__(self):
        return self.title
    daystart = db.DateProperty(default=date.today, required=True)
    dayend = db.DateProperty(default=date.today, required=True)
    monday = db.BooleanProperty(default=True)
    tuesday = db.BooleanProperty(default=True)
    wednesday = db.BooleanProperty(default=True)
    thursday = db.BooleanProperty(default=True)
    friday = db.BooleanProperty(default=True)
    saturday = db.BooleanProperty(default=True)
    sunday = db.BooleanProperty(default=True)
    title = db.StringProperty(required=True)

class Tag(db.Model):
    def __unicode__(self):
        return self.name
    name = db.StringProperty(required=True)

class Article(db.Model):
    def __unicode__(self):
        return self.title
    numid = db.IntegerProperty()
    date = db.DateProperty(default=date.today, required=True)
    title = db.StringProperty(required=True)
    header = db.TextProperty(required=True)
    picname = db.StringProperty()
    piccredits = db.StringProperty(required=True)
    content = db.TextProperty()
    tags = KeyListProperty(Tag)
    
class Friend(db.Model):
    def __unicode__(self):
        return self.desc
    type = db.StringProperty(required=True, choices=set(['places', 'people', 'sites', 'bars']))
    desc = db.TextProperty(required=True)
