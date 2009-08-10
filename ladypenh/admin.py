from django.contrib import admin
from django.forms import ModelForm, FileField, ModelChoiceField
from ladypenh.models import ImageFile, Venue, Event, OneLiner, Article
from google.appengine.api import images
import string


class OneLinerAdmin(admin.ModelAdmin):    
    pass
admin.site.register(OneLiner, OneLinerAdmin)

class ArticleAdmin(admin.ModelAdmin):
    exclude = ('numid', 'legacy_comment_url')
    ordering = ('-date',)
    def save_model(self, request, obj, form, change):
        obj.save()
        if not obj.numid:
            obj.numid = obj.key().id()
            obj.save()
admin.site.register(Article, ArticleAdmin)

class EventForm(ModelForm):
    class Meta:
        model = Event
    pic = FileField(required=False)
    venue = ModelChoiceField(queryset=Venue.gql("WHERE oneshot = FALSE ORDER BY oneshot, name"))


class EventAdmin(admin.ModelAdmin):
    form = EventForm
    fields = ['type', 'venue', 'organizer', 'title', 'date', 'time', 'description',
              'shortdesc', 'pic', 'haslargepic', 'highlight', 'status']
    list_display = ('date', 'time', 'title', 'venue')
    list_display_links = ('title',)
    list_filter = ('venue',)
    ordering = ('-date', 'time')
    #save_as = True / fields not displayed are not copied
    save_on_top = True
    def format_picname(self, filename, date):
        validchars = "-_.%s%s" % (string.ascii_letters, string.digits)
        s = ''.join(c for c in filename if c in validchars)
        return "%s_%s" % (str(date), s)
    def save_model(self, request, obj, form, change):        
        if 'pic' in request.FILES:
            pic = request.FILES['pic']
            blob = pic.read()
            obj.picname = self.format_picname(pic.name, obj.date)
            if obj.haslargepic:
                largepath = "event/large/%s" % obj.picname
                largeobj = ImageFile(name=largepath, blob=blob)
                largeobj.put()
            thumb = images.Image(blob)
            thumb.resize(width=120)
            thumbpath = "event/thumb/%s" % obj.picname
            thumbobj = ImageFile(name=thumbpath, blob=thumb.execute_transforms())
            thumbobj.put()
            obj.picheight = thumb.height
            obj.picwidth = thumb.width
        obj.save()
        if not obj.numid:
            obj.numid = obj.key().id()
            obj.save()
admin.site.register(Event, EventAdmin)


class VenueAdmin(admin.ModelAdmin):
    ordering = ('name',)
admin.site.register(Venue, VenueAdmin)



admin.site.register(ImageFile)

