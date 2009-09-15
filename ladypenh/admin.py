from django.contrib import admin
from django.forms import ModelForm, FileField, ModelChoiceField
from ladypenh.models import ImageFile, Venue, Event, OneLiner, Article, Tag
from google.appengine.api import images
import string

def format_picname(filename, date):
    validchars = "-_.%s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in filename if c in validchars)
    return "%s_%s" % (str(date), s)


class OneLinerAdmin(admin.ModelAdmin):    
    pass
admin.site.register(OneLiner, OneLinerAdmin)

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
            picname = format_picname(pic.name, obj.date)
            picpath = "edito/%s" % picname
            imgobj = ImageFile(name=picpath, blob=pic.read())
            imgobj.put()
            obj.picname = picpath
        obj.save()
        if not obj.numid:
            obj.numid = obj.key().id()
            obj.save()
admin.site.register(Article, ArticleAdmin)


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
        (None, {'fields': ('type', 'venue', 'organizer', 'title', 'date', 'time', 'description',
                           'shortdesc', 'pic', 'haslargepic', 'highlight', 'status')}),
        ('internal', {'fields': ('picname', 'picheight', 'picwidth'), 'classes': ('collapsed',)}))
    list_display = ('date', 'time', 'title', 'venue', 'numid')
    list_display_links = ('title',)
    list_filter = ('venue',)
    ordering = ('-date', 'time')
    save_as = True
    save_on_top = True
    def save_model(self, request, obj, form, change):
        if 'pic' in request.FILES:
            pic = request.FILES['pic']
            blob = pic.read()
            obj.picname = format_picname(pic.name, obj.date)
            if obj.haslargepic:
                largepath = "event/large/%s" % obj.picname
                largeobj = ImageFile(name=largepath, blob=blob)
                largeobj.put()
            thumb = images.Image(blob)
            if thumb.width > 120:
                thumb.resize(width=120)
                blob = thumb.execute_transforms()
            thumbpath = "event/thumb/%s" % obj.picname
            thumbobj = ImageFile(name=thumbpath, blob=blob)
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
admin.site.register(Tag)
