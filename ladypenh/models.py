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
        name = "(no venue)"
        if self.venue != None:
            name = self.venue.name
        return "%s %s, %s (%s) @ %s" % (str(self.date), str(self.time), self.title, self.type, name)
    numid = db.IntegerProperty()
    type = db.StringProperty(required=True, choices=set(['cinema', 'circus', 'concert', 'conference', 'exhibition', 'game', 'party', 'rock', 'sports', 'live_show', 'videogames', 'visit', 'workshop', 'notification']))
    venue = db.ReferenceProperty(Venue)
    organizer = db.StringProperty()
    title = db.StringProperty(required=True)
    date = db.DateProperty(default=date.today, required=True)
    time = db.TimeProperty(default="20:00")
    dayend = db.DateProperty(default=None)
    description = db.TextProperty()
    picname = db.StringProperty()
    haslargepic = db.BooleanProperty(default=False)
    highlight = db.BooleanProperty(default=False)
    monday = db.BooleanProperty(default=False)
    tuesday = db.BooleanProperty(default=False)
    wednesday = db.BooleanProperty(default=False)
    thursday = db.BooleanProperty(default=False)
    friday = db.BooleanProperty(default=False)
    saturday = db.BooleanProperty(default=False)
    sunday = db.BooleanProperty(default=False)

    
class Friend(db.Model):
    def __unicode__(self):
        return self.desc
    type = db.StringProperty(required=True, choices=set(['places', 'people', 'sites', 'bars']))
    desc = db.TextProperty(required=True)
