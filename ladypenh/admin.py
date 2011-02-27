from django.contrib import admin
from django.contrib.auth.models import Message
from django.forms import ModelForm, FileField, ModelChoiceField
from ladypenh.models import Friend, ImageFile, Venue, Event, VenueFile, Tag, Article
from google.appengine.api import images
import string
from datetime import datetime

def format_filename(filename, date=''):
    validchars = "-_.%s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in filename if c in validchars)
    return "%s_%s" % (str(date), s)


class EventForm(ModelForm):
    class Meta:
        model = Event
    pic = FileField(required=False)


class EventAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(EventAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['venue'].queryset = Venue.gql("WHERE oneshot = FALSE ORDER BY oneshot, name")
        return form
    form = EventForm
    fieldsets = (
        (None, {'fields': ('highlight', ('date', 'time'), ('type', 'title'), ('venue', 'organizer'), 'description', ('pic', 'haslargepic'),)}),
        ('Reminders', {'fields': (('dayend', 'hidedayend'), ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'),)}),
        ('Internal', {'fields': ('picname',), 'classes': ('collapsed',)}))
    list_display = ('date', 'time', 'title', 'venue', 'numid')
    list_display_links = ('title',)
    list_filter = ('venue',)
    ordering = ('-date', '-time')
    save_as = True
    save_on_top = True
    def save_model(self, request, obj, form, change):
        if 'pic' in request.FILES:
            pic = request.FILES['pic']
            blob = pic.read()
            obj.picname = format_filename(pic.name, obj.date)
            if obj.haslargepic:
                largepath = "event/large/%s" % obj.picname
                largeobj = ImageFile(name=largepath, blob=blob)
                largeobj.put()
            thumb = images.Image(blob)
            if thumb.width > 200:
                thumb.resize(width=200)
                blob = thumb.execute_transforms()
            thumbpath = "event/thumb/%s" % obj.picname
            thumbobj = ImageFile(name=thumbpath, blob=blob)
            thumbobj.put()
        obj.save()
        if not obj.numid:
            obj.numid = obj.key().id()
            obj.save()
        if obj.date <= datetime.now().date():
            msg = Message(
                user=request.user, 
                message="WARNING: date for %s is today or older! Please make sure the date is ok." % obj.title)
            msg.save()
admin.site.register(Event, EventAdmin)


class VenueAdmin(admin.ModelAdmin):
    ordering = ('name',)
admin.site.register(Venue, VenueAdmin)


class VenueFileAdmin(admin.ModelAdmin):
    exclude = ('filename',)
    def get_form(self, request, obj=None, **kwargs):
        form = super(VenueFileAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['venue'].queryset = Venue.gql("WHERE oneshot = FALSE ORDER BY oneshot, name")
        return form
    def save_model(self, request, obj, form, change):
        if 'blob' in request.FILES:
            blob = request.FILES['blob']
            obj.filename = format_filename(blob.name, datetime.today().date())
        obj.save()
admin.site.register(VenueFile, VenueFileAdmin)

admin.site.register(ImageFile)
admin.site.register(Friend)
admin.site.register(Tag)


class ArticleForm(ModelForm):
    class Meta:
        model = Article
    pic = FileField(required=False)

class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm
    fields = ('date', 'title', 'header', 'pic', 'piccredits', 'content', 'tags')
    ordering = ('-date',)
    list_display = ('date', 'title', 'numid')
    list_display_links = ('title',)
    def save_model(self, request, obj, form, change):
        if 'pic' in request.FILES:
            pic = request.FILES['pic']
            picname = format_filename(pic.name, obj.date)
            picpath = "edito/%s" % picname
            imgobj = ImageFile(name=picpath, blob=pic.read())
            imgobj.put()
            obj.picname = picpath
        obj.save()
        if not obj.numid:
            obj.numid = obj.key().id()
            obj.save()
admin.site.register(Article, ArticleAdmin)

