from ladypenh.models import ImageFile, Venue, Event, OneLiner, Article
from ragendja.dbutils import get_object_list
from datetime import datetime, timedelta


def get_article(day):
    articlelist = Article.gql("WHERE date <= :1 ORDER BY date desc", day).fetch(1)
    if len(articlelist) == 0:
        return None
    return articlelist[0]

def get_articles(day):
    return Article.gql("WHERE date <= :1 ORDER BY date desc", day).fetch(1000)

def get_article_by_id(id):
    articlelist = Article.gql("WHERE numid = :1", int(id)).fetch(1)
    if len(articlelist) == 0:
        return None
    return articlelist[0]

def get_event_by_id(id):
    eventlist = Event.gql("WHERE numid = :1", int(id)).fetch(1)
    if len(eventlist) == 0:
        return None
    return eventlist[0]
    

def get_days(dayspan=0):
    startday = datetime.now().date()
    if dayspan != 0:
        startday += timedelta(days=dayspan)
    days = [startday]
    for i in range(6):
        days.append(days[0] + timedelta(days=i+1))
    return days

def get_events(days):
    events = Event.gql("WHERE date >= :1 and date <= :2 ORDER BY date, time ASC", days[0], days[-1]).fetch(1000)
    return [event for event in events if event.status == 'lp_display']

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
            event.daydiff = (event.date - days[0]).days
            highlights.append(event)
        events[event.date].append(event)
    oneliners_results = OneLiner.gql("WHERE dayspan <= :1 AND dayspan > :2 ORDER BY dayspan, time", days[6], days[0]).fetch(1000)
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
