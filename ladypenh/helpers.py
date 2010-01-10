from ladypenh.models import Friend, Venue, Event, OneLiner, Article, Tag, VenueFile
from ragendja.dbutils import get_object
from datetime import datetime, timedelta
from google.appengine.ext import db
from django.http import Http404


def today(dayspan=0):
    # hack to use Cambodia's tz (everything is UTC on GAE)
    now = datetime.now() + timedelta(hours=7, days=dayspan)
    return now.date()

def get_tags_from_keylist(keylist):
    return [get_object(Tag, tag) for tag in keylist]

def get_article(day):
    articlelist = Article.gql("WHERE date <= :1 ORDER BY date desc", day).fetch(1)
    if len(articlelist) == 0:
        return None, []
    article = articlelist[0]
    return article, get_tags_from_keylist(article.tags)

def get_articles(day, tagstring):
    if tagstring != None:
        tag = Tag.gql("WHERE name = :1", tagstring).fetch(1)[0].key()
        return Article.gql("WHERE date <= :1 AND tags = :2 ORDER BY date desc", day, tag).fetch(1000)
    return Article.gql("WHERE date <= :1 ORDER BY date desc", day).fetch(1000)

def get_article_by_id(id):
    article = get_object(Article, id=int(id))
    return article, get_tags_from_keylist(article.tags)

def get_event_by_id(id):
    return get_object(Event, id=int(id))

def get_venue_by_key(key):
    return get_object(Venue, key)

def get_venue_by_name(venue):
    venuelist = Venue.gql("WHERE ladypenh_url = :1", venue).fetch(1)
    if len(venuelist) == 0:
        raise Http404
    return venuelist[0]

def get_venues():
    return Venue.gql("ORDER BY name").fetch(1000);

def get_days(dayspan=0):
    days = [today(dayspan)]
    for i in range(6):
        days.append(days[0] + timedelta(days=i+1))
    return days

def get_events(days):
    events = Event.gql("WHERE date >= :1 and date <= :2 and status = :3 ORDER BY date, time ASC", 
                       days[0], days[-1], 'lp_display').fetch(1000)
    return events

def add_daydiff_attribute(event, day):
    event.daydiff = (event.date - day).days
    return event

def get_venue_events(days, venue_key):
    events = Event.gql("WHERE date >= :1 and date <= :2 and venue = :3 ORDER BY date, time DESC",
                       days[0], days[-1], venue_key).fetch(1000)
    return [add_daydiff_attribute(event, days[0]) for event in events]

def check_validity(obj, day, attribute):
    if attribute not in dir(obj) or not getattr(obj, attribute):
        return True
    if getattr(obj, attribute) < day:
        return False
    return True

def get_venue_files(days, venue_key):
    files = VenueFile.gql("WHERE venue = :1 ORDER BY valid_until ASC",
                          venue_key).fetch(1000)
    return [file for file in files if check_validity(file, days[0], 'valid_until')]
    

def get_friends():
    friends = {}
    friends_result = Friend.gql("").fetch(1000)
    for friend in friends_result:
        if friend.type not in friends:
            friends[friend.type] = []
        friends[friend.type].append(friend)
    return friends

def get_daysinfo_and_highlights(days):
    events = {}
    oneliners = {}
    for day in days:
        events[day] = []
        oneliners[day] = []
    highlights = []
    query_results = Event.gql("WHERE date >= :1 AND date <= :2 ORDER BY date ASC, time ASC", days[0], days[-1]).fetch(1000)
    for event in query_results:
        if event.status != "lp_display":
            continue
        if event.highlight:
            add_daydiff_attribute(event, days[0])
            highlights.append(event)
        events[event.date].append(event)
    oneliners_results = OneLiner.gql("ORDER BY title").fetch(1000)
    for oneliner in oneliners_results:
        for day in days:
            if oneliner.daystart <= day and oneliner.dayend >= day:
                if oneliner.daycode == 0:
                    oneliners[day].append(oneliner)
                    continue
                isdayin = str(day.isoweekday()) in str(oneliner.daycode)
                if (oneliner.daycode < 0 and not isdayin) or (oneliner.daycode > 0 and isdayin):
                    oneliners[day].append(oneliner)
    daysinfo = []
    for day in days:
        daysinfo.append((day, events[day], oneliners[day]))
    return daysinfo, highlights[:5]


def get_theme(day):
    return "default"

def get_tags():
    return Tag.gql("ORDER BY name").fetch(1000)
