from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Tag)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Label)
admin.site.register(Genre)
admin.site.register(Style)
admin.site.register(TagShareRequest)