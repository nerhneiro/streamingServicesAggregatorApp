from django.contrib import admin
from authapp.models import SiteUser, FriendRequest
# Register your models here.
admin.site.register(SiteUser)
admin.site.register(FriendRequest)