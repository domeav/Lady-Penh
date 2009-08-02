from django.contrib import admin
from ladypenh.models import ImageFile, Venue, Event, OneLiner, Article
from google.appengine.api import images
import string

def date_to_datetime(d, dayspan=0):
    d += timedelta(dayspan)
    return datetime(d.year, d.month, d.day)

class OneLinerAdmin(admin.ModelAdmin):    
    exclude = ('dayspan',)
    def save_model(self, request, obj, form, change):
        # as of 30/07/09, I have to do this - see http://appengine-cookbook.appspot.com/attachment/?id=ahJhcHBlbmdpbmUtY29va2Jvb2tyEQsSCkF0dGFjaG1lbnQY0ygM
        # and I can't just store dates in my list because they are supposed to be converted to datetime before being stored
        obj.dayspan = [date_to_datetime(obj.daystart), date_to_datetime(obj.dayend, 1)]
        obj.save()
admin.site.register(OneLiner, OneLinerAdmin)

class ArticleAdmin(admin.ModelAdmin):
    exclude = ('numid', 'legacy_comment_url')
admin.site.register(Article, ArticleAdmin)

class EventAdmin(admin.ModelAdmin):
    exclude = ('numid', 'picname', 'picheight', 'picwidth')
    def format_picname(self, filename, date):
        validchars = "-_.%s%s" % (string.ascii_letters, string.digits)
        s = ''.join(c for c in filename if c in validchars)
        return "%s_%s" % (str(date), s)
    def save_model(self, request, obj, form, change):
        obj.picname = self.format_picname(request.FILES['pic'].name, obj.date)
        if obj.haslargepic:
            largepath = "event/large/%s" % obj.picname
            largeobj = ImageFile(name=largepath, blob=obj.pic)
            largeobj.put()
        thumb = images.Image(obj.pic)
        thumb.resize(width=120)
        thumbpath = "event/thumb/%s" % obj.picname
        thumbobj = ImageFile(name=thumbpath, blob=thumb.execute_transforms())
        thumbobj.put()
        obj.picheight = thumb.height
        obj.picwidth = thumb.width
        obj.pic = None
        obj.save()
        obj.numid = obj.key().id()
        obj.save()

admin.site.register(Event, EventAdmin)


for model in [ImageFile, Venue]:
    admin.site.register(model)

