from ladypenh.models import Friend, Venue, Event, VenueFile, Article, Tag, AdImageLink
from ragendja.dbutils import get_object
from datetime import datetime, timedelta
from google.appengine.ext import db
from django.http import Http404
from google.appengine.api import memcache


def use_cache(fn):
    '''Cache decorator, to be used with django view functions. request object 
    must be the first argument.'''
    def cached_execution(request, **args):
        response = None
        if not request.user.is_authenticated():
            response = memcache.get(request.path)
        if response is not None:
            return response
        response = fn(request, **args)
        if not request.user.is_authenticated():
            memcache.set(request.path, response, 7200)        
        return response
    return cached_execution
        


def today(dayspan=0):
    # hack to use Cambodia's tz (everything is UTC on GAE)
    now = datetime.now() + timedelta(hours=7, days=dayspan)
    return now.date()


def get_ads():
    adList = AdImageLink.gql("").fetch(1000)
    ads = {}
    for ad in adList:
        ads[ad.name] = ad
    return ads


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
    return Venue.gql("WHERE oneshot = :1 ORDER BY name", False).fetch(1000);

def get_days(dayspan=0, nbdays=7):
    days = [today(dayspan)]
    for i in range(nbdays - 1):
        days.append(days[0] + timedelta(days=i+1))
    return days

# can be called with either a single day, or a list of consecutive days
def get_events(day):
    events = None
    if type(day) == list:
        # assuming this is a list of days
        return Event.gql("WHERE date >= :1 and date <= :2 ORDER BY date, time ASC", day[0], day[-1]).fetch(1000)

    events = Event.gql("WHERE date = :1 ORDER BY time ASC", day).fetch(1000)
    # put events with no time defined at the end
    eventslist = []
    events_notime = []
    for event in events:
        if event.time:
            eventslist.append(event)
        else :
            events_notime.append(event)
    return eventslist + events_notime
        

def get_reminders(day):
    dayname = day.strftime("%A").lower()
    reminders = Event.gql("WHERE dayend >= :1 AND %s = :2" % dayname,
                          day, True).fetch(1000)
    time = []
    notime = []
    for r in reminders:
        if r.date >= day:
            continue
        if r.time:
            time.append(r)
        else:
            notime.append(r)
    time.sort(key=lambda r: r.time)
    return time + notime

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

weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def get_highlights(days):
    events = Event.gql("WHERE date >= :1 AND date <= :2 AND highlight = :3 ORDER BY date ASC, time ASC", days[0], days[-1], True).fetch(1000)
    return [add_daydiff_attribute(event, days[0]) for event in events]


def get_theme(day):
    return "default"


def get_article(day):
    articlelist = Article.gql("WHERE date <= :1 ORDER BY date desc", day).fetch(1)
    if len(articlelist) == 0:
        return None, []
    article = articlelist[0]
    if (day - article.date).days > 2:
        return None, []
    return article, get_tags_from_keylist(article.tags)

def get_articles(day, tagstring):
    if tagstring != None:
        tag = Tag.gql("WHERE name = :1", tagstring).fetch(1)[0].key()
        return Article.gql("WHERE date <= :1 AND tags = :2 ORDER BY date desc", day, tag).fetch(1000)
    return Article.gql("WHERE date <= :1 ORDER BY date desc", day).fetch(1000)

def get_article_by_id(id):
    article = get_object(Article, id=int(id))
    return article, get_tags_from_keylist(article.tags)

def get_tags():
    return Tag.gql("ORDER BY name").fetch(1000)

def get_tags_from_keylist(keylist):
    return [get_object(Tag, tag) for tag in keylist]
