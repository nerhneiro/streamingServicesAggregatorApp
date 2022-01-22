from django.db import models
from django.contrib.auth.models import AbstractUser
from mainapp.models import Album

class SiteUser(AbstractUser):
    avatar = models.ImageField(upload_to='users_avatars', blank=True)
    age = models.PositiveIntegerField(verbose_name='age', null=True, blank=True)
    albums = models.ManyToManyField(Album, verbose_name='albums', blank=True, related_name='album_users')
    email = models.EmailField(unique=True, verbose_name='email')
    country = models.CharField(max_length=128, blank=True, null=True, verbose_name='country')
    passwordYM = models.CharField(max_length=1024, blank=True, verbose_name='Yandex Music password')
    emailYM = models.EmailField(max_length=128, null=True, blank=True, verbose_name='yandex Music email')
    passwordSP = models.CharField(max_length=1024, null=True, blank=True, verbose_name='Spotify password')
    idSP = models.CharField(max_length=1024, blank=True, verbose_name='Spotify user id')
    clientIdSP = models.CharField(max_length=1024, blank=True, verbose_name='Spotify client id project')
    clientSecretSP = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Client secret Spotify project")
    tokenAccessSP = models.CharField(max_length=1024, null=True, blank=True, verbose_name='Spotify access token')
    tokenRefreshSP = models.CharField(max_length=1024, null=True, blank=True, verbose_name='Spotify refresh token')
    tokenReserveSP = models.CharField(max_length=1024, null=True, blank=True, verbose_name='Spotify reserve token')
    codeSP = models.CharField(max_length=1024, null=True, blank=True, verbose_name='Spotify code')
    redirectUriSP = models.CharField(max_length=1024, null=True, blank=True, verbose_name='Spotify redirect uri project')
    emailSP = models.EmailField(max_length=128, null=True, blank=True, verbose_name='Spotify email')
    passwordVK = models.CharField(max_length=1024, blank=True, verbose_name='VK password')
    idVK = models.CharField(max_length=1024, blank=True, verbose_name='VK id')
    tokenVK = models.CharField(max_length=1024, blank=True, verbose_name='VK token')
    emailVK = models.EmailField(max_length=128, blank=True, verbose_name='VK email')
    numberVK = models.PositiveIntegerField(verbose_name='VK number', null=True, blank=True)
    friends = models.ManyToManyField("SiteUser", blank=True, related_name="friend_to")
    friendRequests = models.ManyToManyField("FriendRequest", blank=True, related_name="to_this_user")

class FriendRequest(models.Model):
    user_from = models.ForeignKey("SiteUser", null=True, verbose_name='request from', on_delete=models.CASCADE, related_name='user_from')
    user_to = models.ForeignKey("SiteUser", null=True, verbose_name='request to', on_delete=models.CASCADE, related_name='user_to')
    accepted = models.BooleanField(default=False, verbose_name='friend request accepted')