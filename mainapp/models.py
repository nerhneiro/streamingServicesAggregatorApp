from django.db import models

# Create your models here.
class Tag(models.Model):
    name = models.CharField(verbose_name="Tag's name", max_length=128)
    user_pk = models.PositiveIntegerField(verbose_name='user_pk', default=0)
    user_from_pk = models.PositiveIntegerField(verbose_name='user_from_pk', default=0)

class TagShareRequest(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name='tags',related_name='requests', blank=True)
    user_from_pk = models.PositiveIntegerField(verbose_name='User from pk', default=0)
    user_to_pk = models.PositiveIntegerField(verbose_name='User to pk', default=0)


class Artist(models.Model):
    idDiscogs = models.PositiveIntegerField(verbose_name="DiscogsID артиста")
    idYandexMusic = models.CharField(verbose_name="Artist yandex music id", max_length=128, blank=True)
    idSpotify = models.CharField(verbose_name="Spotify id", max_length=128, blank=True)
    name = models.CharField(verbose_name="Artist's name", max_length=128)

class Label(models.Model):
    name = models.CharField(verbose_name="Label's name", max_length=128)
    idDiscogs = models.PositiveIntegerField(verbose_name="DiscogsID")

class Genre(models.Model):
    name = models.CharField(verbose_name='genre', max_length=128)

class Style(models.Model):
    name = models.CharField(verbose_name='style', max_length=128)

SERVERS_CHOICES = [
    ('YM', 'Yandex Music'),
    ('SP', 'Spotify'),
    ('VK', 'VK')
]

class Album(models.Model):
    source = models.CharField(choices=SERVERS_CHOICES, default='YM', max_length=2)
    idYandex = models.PositiveIntegerField(verbose_name="YandexMusicID", default=0)
    idDiscogs = models.PositiveIntegerField(verbose_name="DiscogsID")
    idDiscogsSecondary = models.PositiveIntegerField(verbose_name="DiscogsSecondaryID", null=True)
    idSpotify = models.CharField(verbose_name="Spotify id", max_length=1024, default='-1')
    name = models.CharField(verbose_name="Album's name", max_length=128)
    imageURL = models.CharField(verbose_name='Image url', max_length=512, default='', null=True)
    artists = models.ManyToManyField(Artist, verbose_name="Artists", blank=True, related_name='albums')
    tags = models.ManyToManyField(Tag, related_name="tagged_albums", blank=True)
    labels = models.ManyToManyField(Label, related_name="labeled_albums", blank=True)
    genres = models.ManyToManyField(Genre, related_name='genred_albums', blank=True)
    styles = models.ManyToManyField(Style, related_name='styled_albums', blank=True)
    cover = models.ImageField(width_field=100, height_field=100, blank=True)
    year = models.PositiveIntegerField(verbose_name='year', default=0)
