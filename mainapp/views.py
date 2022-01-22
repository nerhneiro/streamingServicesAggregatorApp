from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import Album, Artist, Label, Tag, Genre, Style, TagShareRequest
from yandex_music.client import Client
import authapp.requestsYandexDiscogs as ryd
from django.shortcuts import redirect
import authapp.secret as secret
from django.db.models import Q
from mainapp.forms import yearSortForm, addTagForm, friendRequestForm, friendRequestConfirmForm, shareTagsForm
from authapp.models import SiteUser, FriendRequest
# from google_trans_new import google_translator
from PIL import Image
import requests, base64
from pathlib import Path
import time
import wikipedia
from django.views import View
from django.views.generic import ListView, DetailView
# from .filters import AlbumFilter
# Create your views here.
def main(request):
    if request.user.is_authenticated:
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
        authenticated = True
    else:
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'
        authenticated = False
    context = {
        'title': 'Main',
        'username': username,
        'log_message': log_message,
        'log_link': log_link,
        'authenticated': authenticated,
    }
    return render(request, 'mainapp/index.html', context)

def connected(request):
    yandexMusicConnected = False
    spotifyConnected = False
    yandexEmail = ''
    spotifyClientId = ''
    if request.user.is_authenticated:
        username = request.user.username
        authenticated = True
        log_link = 'auth:logout'
        log_message = 'Log out'
        if request.user.emailYM != (None or '') and request.user.passwordYM != (None or '') :
            yandexMusicConnected = True
            yandexEmail = request.user.emailYM
        if request.user.clientIdSP != (None or ''):
            spotifyConnected = True
            spotifyClientId = request.user.clientIdSP
    else:
        username = ''
        authenticated = False
        log_link = 'auth:login'
        log_message = 'Log in'
    context = {
        'title': 'Connected accounts',
        'username': username,
        'authenticated': authenticated,
        'yandexMusicConnected': yandexMusicConnected,
        'log_message': log_message,
        'log_link': log_link,
        'spotifyConnected': spotifyConnected,
        'spotifyClientId': spotifyClientId,
        'yandexEmail': yandexEmail,
    }
    return render(request, 'mainapp/connectedaccounts.html', context)



def playlists(request):
    yandexMusicConnected = False
    spotifyConnected = False
    form = None
    username = ''
    if request.user.is_authenticated:
        albums = request.user.albums.all()
        authenticated = True
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
        username = request.user.username
        if request.user.emailYM != (None or '') and request.user.passwordYM != (None or ''):
            yandexMusicConnected = True
        if request.user.clientIdSP != (None or '') :
            spotifyConnected = True
        if request.user.emailYM != (None or '') and request.user.passwordYM != (None or '') or request.user.clientIdSP != (None or '') :
                if request.method == 'POST':
                    form = yearSortForm(request.user, request.POST)
                    if form.is_valid():
                        print("GENRES: ", form.cleaned_data['genres'])
                        if (form.cleaned_data['search_all'] == False):
                            # если флажок all the fields required не нажат
                            albums = Album.objects.all().filter(album_users=request.user)
                            albumsYear = albums.filter(year=form.cleaned_data['year'])
                            albumsStyles = []
                            albumsGenres = []
                            albumsLabels = []
                            albumsTags = []
                            albumsArtists = []
                            albumsUsersTags = set()
                            if form.cleaned_data['styles'] != None:
                                #получение стилей для сортировки
                                albumsStyles = albums.filter(styles__in=form.cleaned_data['styles'])
                            if form.cleaned_data['genres'] != None:
                                # получение жанров для сортировки
                                albumsGenres = albums.filter(genres__in=form.cleaned_data['genres'])
                            if form.cleaned_data['labels'] != None:
                                # получение лейблов для сортировки
                                albumsLabels = albums.filter(labels__in=form.cleaned_data['labels'])
                            if form.cleaned_data['tags'] != None:
                                # получение тегов для сортировки
                                albumsTags = albums.filter(tags__in=form.cleaned_data['tags'])
                            if form.cleaned_data['users_tags'] != None:
                                # получение пользователей для сортировки
                                users_tuple = form.cleaned_data['users_tags']
                                for user_from_id in users_tuple:
                                    albumsUsersTags |= set(albums.filter(tags__user_from_pk=user_from_id, tags__user_pk=request.user.pk))
                                    print("USERS_TUPLE: ", form.cleaned_data['users_tags'])
                            if form.cleaned_data['artists'] != None:
                                albumsArtists = albums.filter(artists__in=form.cleaned_data['artists'])


                            albums = set([])
                            albums |= set(albumsYear)
                            albums |= set(albumsStyles)
                            albums |= set(albumsGenres)
                            albums |= set(albumsLabels)
                            albums |= set(albumsTags)
                            albums |= set(albumsArtists)
                            print("ALBUM USERS TAGS: ", albumsUsersTags)
                            albums |= set(albumsUsersTags)
                            print(albums)
                        else:
                            # если год не указан
                            if form.cleaned_data['year'] != None:
                                albums = Album.objects.all().filter(album_users=request.user,
                                                                    year=form.cleaned_data['year'])
                            else:
                                albums = Album.objects.all().filter(album_users=request.user)
                            if len(form.cleaned_data['styles']) != 0:
                                for style in form.cleaned_data['styles']:
                                    albums = albums.filter(styles=style)
                            if len(form.cleaned_data['genres']) != 0:
                                albums = albums.filter(genres__in=form.cleaned_data['genres'])
                            if len(form.cleaned_data['labels']) != 0:
                                albums = albums.filter(labels__in=form.cleaned_data['labels'])
                            if len(form.cleaned_data['tags']) != 0:
                                albums = albums.filter(tags__in=form.cleaned_data['tags'])
                            if len(form.cleaned_data['artists']) != 0:
                                albums = albums.filter(artists__in=form.cleaned_data['artists'])
                            if len(form.cleaned_data['users_tags']) != 0:
                                users_tuple = form.cleaned_data['users_tags']
                                for user_from_id in users_tuple:
                                    albums = albums.filter(tags__user_from_pk=user_from_id)

                            albums = set(albums)
                        print("ALBUMS: ", albums)
                else:
                    form = yearSortForm(request.user)

                    print("CREATE FORM")
                    albums = Album.objects.all().filter(album_users=request.user)
        else:
            albums = []
    else:
        albums = []
        authenticated = False
        log_link = 'auth:login'
        log_message = 'Log in'
    context = {
        'title': 'Playlists',
        'albums': albums,
        'username': username,
        'form': form,
        'yandexMusicConnected': yandexMusicConnected,
        'log_message': log_message,
        'log_link': log_link,
        'authenticated': authenticated,
        'spotifyConnected': spotifyConnected,
    }
    return render(request, 'mainapp/playlists.html', context)

def fillInDBYandexMusic(albums, user):
    albumsIdYM = set()
    for al in albums:
        artists = []
        for ar in al['album']['artists']:
            artists.append((ar['name'], ar['id']))
        album = al['album']['title']
        idYM = al['album']['id']
        albumsIdYM.add(idYM)
        image_url = 'http://' + al['album']['cover_uri'][:-2] + '300x300'
        try:
            albumExisting = Album.objects.get(idYandex=int(idYM))
            try:
                album = user.albums.get(idYandex=idYM)
            except:
                user.albums.add(albumExisting)
        except:
            artists, year, genres, styles, labels, idDiscogs = ryd.get_info(album, artists)
            albumNew = Album.objects.create(source='YM', idYandex=idYM, idDiscogs=idDiscogs, name=album, year=year)
            albumNew.save()
            if genres != None:
                for g in genres:
                    try:
                        genre = Genre.objects.get(name=g)
                        albumNew.genres.add(genre)
                    except:
                        genreNew = Genre.objects.create(name=g)
                        genreNew.save()
                        albumNew.genres.add(genreNew)
            if labels != None:
                for l, id in labels:
                    try:
                        label = Label.objects.get(name=l)
                        albumNew.labels.add(label)
                    except:
                        labelNew = Label.objects.create(name=l, idDiscogs=id)
                        labelNew.save()
                        albumNew.labels.add(labelNew)
            if styles != None:
                for s in styles:
                    try:
                        style = Style.objects.get(name=s)
                        albumNew.styles.add(style)
                    except:
                        styleNew = Style.objects.create(name=s)
                        styleNew.save()
                        albumNew.styles.add(styleNew)
            if artists != None:
                print("IN ARTISTS")
                print(artists)
                for ar, idInitial, idDisc in artists:
                    print("HERE 1")
                    try:
                        print("HERE 2")
                        artist = Artist.objects.get(idDiscogs=idDisc)
                        albumNew.artists.add(artist)
                    except:
                        print("HERE 3")
                        artistNew = Artist.objects.create(name=ar, idDiscogs=idDisc, idYandexMusic=idInitial)
                        artistNew.save()
                        albumNew.artists.add(artistNew)
            albumNew.imageURL = image_url
            albumNew.save()
            user.albums.add(albumNew)
    albumsIdDB = set()
    # получаем альбомы Яндекс Музыки, которые нужно удалить (они были в медиатеке до апдейта, но пользователь их удалил из любимых)
    for i in user.albums.filter(idSpotify='-1'):
        albumsIdDB.add(i.idYandex)
    albumsRemove1 = albumsIdYM - albumsIdDB
    albumsRemove2 = albumsIdDB - albumsIdYM
    albumsRemove = albumsRemove1.union(albumsRemove2)
    for i in albumsRemove:
        alb = user.albums.get(idYandex=i)
        if len(list(alb.tags.filter(~Q(user_from_pk=user.pk)))) == 0:
            for t in alb.tags.filter(user_from_pk=user.pk).all():
                alb.tags.remove(t)
            user.albums.remove(alb)

def fillInDBSpotify(albums, user):
    albumsIdSP = set()
    for al in albums:
        id = al['album']['id']
        name = al['album']['name']
        image_url = al['album']['images'][0]['url']
        albumsIdSP.add(id)
        try:
            album = Album.objects.get(idSpotify=id)
            try:
                album_user = user.albums.get(idSpotify=id)
            except:
                user.albums.add(album)
        except:
            artists = []
            for ar in al['album']['artists']:
                ar_id = ar['id']
                ar_name = ar['name']
                artists.append((ar_name, ar_id))
            artists, year, genres, styles, labels, idDiscogs = ryd.get_info(name, artists)
            albumNew = Album.objects.create(source='SP', idSpotify=id, idDiscogs=idDiscogs, name=name, year=year)
            albumNew.save()
            if genres != None:
                for g in genres:
                    try:
                        genre = Genre.objects.get(name=g)
                        albumNew.genres.add(genre)
                    except:
                        genreNew = Genre.objects.create(name=g)
                        genreNew.save()
                        albumNew.genres.add(genreNew)
            if labels != None:
                for l, id in labels:
                    try:
                        label = Label.objects.get(name=l)
                        albumNew.labels.add(label)
                    except:
                        labelNew = Label.objects.create(name=l, idDiscogs=id)
                        labelNew.save()
                        albumNew.labels.add(labelNew)
            if styles != None:
                for s in styles:
                    try:
                        style = Style.objects.get(name=s)
                        albumNew.styles.add(style)
                    except:
                        styleNew = Style.objects.create(name=s)
                        styleNew.save()
                        albumNew.styles.add(styleNew)
            if artists != None:
                print("IN ARTISTS")
                print(artists)

                for ar, idInitial, id_discogs in artists:
                    print("HERE 1")
                    try:
                        print("HERE 2")
                        artist = Artist.objects.get(idDiscogs=id_discogs)
                        albumNew.artists.add(artist)
                    except:
                        print("HERE 3")
                        artistNew = Artist.objects.create(name=ar, idSpotify=idInitial, idDiscogs=id_discogs)
                        artistNew.save()
                        albumNew.artists.add(artistNew)
            albumNew.imageURL = image_url
            albumNew.save()
            user.albums.add(albumNew)
    albumsIdDB = set()
    print(user.albums.filter(idYandex=0))
    #получаем альбомы Spotify, которые нужно удалить (они были в медиатеке до апдейта, но пользователь их удалил из любимых)
    for i in user.albums.filter(idYandex=0):
        albumsIdDB.add(i.idSpotify)
    albumsRemove1 = albumsIdSP - albumsIdDB
    albumsRemove2 = albumsIdDB - albumsIdSP
    albumsRemove = albumsRemove1.union(albumsRemove2)
    for i in albumsRemove:
        alb = user.albums.get(idSpotify=i)
        if len(list(alb.tags.filter(~Q(user_from_pk=user.pk)))) == 0:
            user.albums.remove(alb)

#функция для получения альбома из аккаунта Spotify
def get_albums(token):
    url = 'https://api.spotify.com/v1/me/albums'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    r = requests.get(url, headers=headers)
    response = r.json()
    return response

#функция для refresh'а токена для запросов к Spotify
def refresh(refresh_token, base_64):
    query = "https://accounts.spotify.com/api/token"

    response = requests.post(query,
                             data={"grant_type": "refresh_token",
                                   "refresh_token": refresh_token},
                             headers={"Authorization": "Basic " + base_64})

    response_json = response.json()
    print("REFRESH RESPONSE: ", response_json)

    return response_json["access_token"]

def updateDB(request):
    #Yandex Music account update
    if request.user.is_authenticated and request.user.emailYM != (None or '') and request.user.passwordYM != (None or ''):
        try:
            user = request.user
            password = secret.dehash(user.passwordYM)
            print("PASSWORD ", user.passwordYM)
            # client = Client.from_credentials(user.emailYM, user.passwordYM)
            client = Client.from_credentials(user.emailYM, password)
            albums = client.users_likes_albums()
            try:
                fillInDBYandexMusic(albums, user)
            except:
                print("YOU ARE MAKING REQUESTS TOO QUICKLY")
                time.sleep(5)
                fillInDBYandexMusic(albums, user)
        except:
            time.sleep(5)
            user = request.user
            password = secret.dehash(user.passwordYM)
            client = Client.from_credentials(user.emailYM, password)
            albums = client.users_likes_albums()
            try:
                fillInDBYandexMusic(albums, user)
            except:
                print("ERROR")
                pass
    #Spotify account update
    if request.user.is_authenticated and request.user.clientIdSP != (None or '') :
        client_secret = secret.dehash(request.user.clientSecretSP)
        client_id = request.user.clientIdSP
        client_creds = f"{client_id}:{client_secret}"
        client_creds_64 = base64.b64encode(client_creds.encode())
        albums = []
        try:
            albums = get_albums(request.user.tokenAccessSP)['items']
            for album_sp in albums:
                print(album_sp['album']['name'])
            print(len(albums))
        except:
            try:
                request.user.tokenAccessSP = refresh(request.user.tokenRefreshSP, client_creds_64.decode())
                albums = get_albums(request.user.tokenAccessSP)['items']
                for album_sp in albums:
                    print(album_sp['album']['name'])
                print(len(albums))
            except:
                print("COULDN'T REFRESH AN ACCESS TOKEN")
        print("READY TO FILL IN DB")
        try:
            fillInDBSpotify(albums, request.user)
        except:
            print("AN ERROR IN SPOTIFY DB FILLING OCCURRED")

    return redirect('mainapp:playlists')

def account(request):
    if request.user.is_authenticated:
        username = request.user.username
        yandexMusicConnected = False
        spotifyConnected = False
        if request.user.passwordYM != (None or '') and request.user.emailYM != (None or ''):
            yandexMusicConnected = True
        if request.user.clientIdSP != (None or ''):
            spotifyConnected = True
        context = {
            'title': 'Account',
            'user': request.user,
            'username': username,
            'yandexMusicConnected': yandexMusicConnected,
            'spotifyConnected': spotifyConnected,
        }
        return render(request, 'mainapp/account.html', context)
    else:
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

def playlist(request, pk=None):
    if request.user.is_authenticated:
        authenticated = True
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
    else:
        authenticated = False
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'
    album = Album.objects.get(pk=int(pk))
    genresLength = len(album.genres.all())
    genresLengthLeft = genresLength - 4
    if len(album.genres.all()) >= 4:
        genresArray = [album.genres.all()[x] for x in range(0, 4)]
    else:
        genresArray = album.genres.all()
    genresLeftArray = [album.genres.all()[x] for x in range(4, genresLength)]
    image = ''
    if album.source == 'YM':
        image = album.imageURL[:-7] + "300x300"
    if album.source == 'SP':
        image = album.imageURL
    #КОГДА-НИБУДЬ Я ПОПЛАЧУСЬ ЗА ТО, ЧТО ПРИПИСЫВАЮ PK К НАЗВАНИЮ ТЕГА
    #UPDATE: уже не приписываю
    if request.method == 'POST':
        form = addTagForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['tag_name']
            if request.POST.get('add'):
                tag_found = Tag.objects.all().filter(name=name, user_pk=request.user.pk, user_from_pk=request.user.pk)
                if len(tag_found) == 0:
                    tag = Tag.objects.create(name=name, user_pk=request.user.pk, user_from_pk=request.user.pk)
                    tag.save()
                else:
                    tag = tag_found[0]
                album = Album.objects.get(pk=pk)
                album.tags.add(tag)
                album.save()
                album_another = None
                if album.idYandex == 0:
                    try:
                        album_another = request.user.albums.get(idDiscogs=album.idDiscogs, idSpotify='-1')
                    except:
                        album_another = None
                if album.idSpotify == '-1':
                    try:
                        album_another = request.user.albums.get(idDiscogs=album.idDiscogs, idYandex=0)
                    except:
                        album_another = None
                if album_another != None:
                    if tag not in list(album_another.tags.all()):
                        album_another.tags.add(tag)
                        album_another.save()

            elif request.POST.get('delete'):
                print("HERE4")
                tag_found = Tag.objects.all().filter(name=name, user_pk=request.user.pk, user_from_pk=request.user.pk)
                if len(tag_found) != 0:
                    tag_found = tag_found[0]
                    print("TAG_FOUND: ", tag_found)
                    album = Album.objects.get(pk=pk)
                    album.tags.remove(tag_found)
                    album_another = None
                    if album.idYandex == 0:
                        try:
                            album_another = request.user.albums.get(idDiscogs=album.idDiscogs, idSpotify='-1')
                        except:
                            album_another = None
                    if album.idSpotify == '-1':
                        try:
                            album_another = request.user.albums.get(idDiscogs=album.idDiscogs, idYandex=0)
                        except:
                            album_another = None
                    if album_another != None:
                        if tag_found in list(album_another.tags.all()):
                            album_another.tags.remove(tag_found)
                            album_another.save()

                    if len(list(Album.objects.filter(tags=tag_found))) == 0:
                        tag_found.delete()

    else:
        form = addTagForm()
    album = Album.objects.get(pk=pk)
    tags_mine = album.tags.filter(user_pk=request.user.pk, user_from_pk=request.user.pk)
    tags_from_friends = album.tags.filter(user_pk=request.user.pk).exclude(user_from_pk=request.user.pk)

    source = 0
    if album.source == 'YM':
        source = 1
    if album.source == 'SP':
        source = 2
    context = {
        'username': username,
        'album': album,
        'genresLength': genresLength,
        'genresLengthLeft': genresLengthLeft,
        'genresLeftArray': genresLeftArray,
        'genresArray': genresArray,
        'log_message': log_message,
        'log_link': log_link,
        'image': image,
        'form': form,
        'tags_mine': tags_mine,
        'tags_from_friends': tags_from_friends,
        'authenticated': authenticated,
        'source': source,
    }

    return render(request, 'mainapp/playlist.html', context)

def sendFriendRequest(request, id):
    user = get_object_or_404(SiteUser, id=id)
    frequest, created = FriendRequest.objects.get_or_create(
        user_from=request.user,
        user_to=user)
    return HttpResponseRedirect('/friends/')

def acceptFriendRequest(request, id):
    print("Friend request ACCEPTED")
    user_from = SiteUser.objects.get(pk=id)
    frequest = FriendRequest.objects.filter(user_from=user_from, user_to=request.user).first()
    user1 = frequest.user_to
    user2 = user_from
    user1.friends.add(user2)
    user2.friends.add(user1)
    if (FriendRequest.objects.filter(user_from=request.user, user_to=user_from).first()):
        request_rev = FriendRequest.objects.filter(fuser_from=request.user, user_to=user_from).first()
        request_rev.delete()
    frequest.delete()
    return HttpResponseRedirect('/friends/')

#отклонение запроса в друзья (пользователем, который его получил)
def declineFriendRequest(request, id):
    user_from = SiteUser.objects.get(pk=id)
    frequest = FriendRequest.objects.filter(user_from=user_from, user_to=request.user).first()
    frequest.delete()
    return HttpResponseRedirect('/friends/')

#отмена запроса в друзья (пользователем, который его отправил)
def cancelFriendRequest(request, id):
    user = get_object_or_404(SiteUser, id=id)
    frequest = FriendRequest.objects.all().filter(
        user_from=request.user,
        user_to=user).first()
    frequest.delete()
    return HttpResponseRedirect('/friends/')

#удаление пользователя из друзей
def deleteFriend(request, id):
    user = request.user
    friend = get_object_or_404(SiteUser, id=id)
    user.friends.remove(friend)
    friend.friends.remove(user)
    frequest = FriendRequest(user_from=friend, user_to=user)
    frequest.save()
    return HttpResponseRedirect('/friends/')

def shareTag(request, id):
    user = request.user
    friend = get_object_or_404(SiteUser, id=id)
    frequest = FriendRequest(user_from=friend, user_to=user)
    frequest.save()
    return HttpResponseRedirect('/friends/')

#отклонение запроса на шеринг тегами (пользователем, к которому он отправил)
def declineTags(request, id):
    try:
        reqTags = TagShareRequest.objects.get(pk=id)
        reqTags.delete()
    except:
        pass
    return HttpResponseRedirect('/friends/')

user_pk_to = 0
def shareTags(request, id):
    global user_pk_to
    authenticated = request.user.is_authenticated
    username = request.user.username
    message = ''
    if request.method == 'POST':
        form = shareTagsForm(request.user, request.POST)
        if form.is_valid():
            #получение id/pk пользователя, с которым делимся тегами
            # print("PATH: ", request.path, " FULL PATH: ", request.get_full_path(), " ID: ", id, " USER PK TO: ", user_pk_to, " ABSOLUTE: ", request.build_absolute_uri())
            user_to = SiteUser.objects.get(id=user_pk_to) #объект SiteUser, с которым делимся тегами
            tags = form.cleaned_data['tags']

            #проверка, что пользоваетель у нас в друзьях
            in_friends = False
            print(user_to)
            for u in request.user.friends.all():
                print(u.username, user_to.username)
                if u.username == user_to.username:
                    in_friends = True
            print("FRIEND: ", in_friends)
            #проверяем, что друг подключил аккаунт Яндекс Музыки или Spotify
            if (user_to.passwordYM != (None or '')  and user_to.emailYM != (None or '') or user_to.clientIdSP != (None or '')) and not (user_to == request.user):
                    tagShareRequest = TagShareRequest.objects.filter(user_to_pk=user_pk_to, user_from_pk=request.user.pk)
                    tagReq_exists = False
                    for t in tagShareRequest.all():
                        if list(t.tags.all()) == list(tags.all()):
                            tagReq_exists = True
                    if not tagReq_exists:
                        tagShareRequest = TagShareRequest(user_to_pk=user_pk_to, user_from_pk=request.user.pk)
                        tagShareRequest.save()
                        for t in tags.all():
                            tagShareRequest.tags.add(t)
                        tagShareRequest.save()
                    return HttpResponseRedirect('/friends/')
            if user_to.passwordYM == (None or '') and user_to.emailYM == (None or '') and user_to.clientIdSP == (None or ''):
                message = f'{user_to.username} hasn\'t connected any streaming service\'s account yet. You can\'t share tags with this user'
    else:
        form = shareTagsForm(request.user)
        user_pk_to = id
        print("form shareTagsForm")
    context = {
        'form': form,
        'user': request.user,
        'authenticated': authenticated,
        'username': username,
        'message': message,
        'log_message': 'Log out',
    }
    return render(request, 'mainapp/shareTag.html', context)

#переход в раздел альбомов по тегу
def playlistTags(request, id):
    yandexMusicConnected = False
    spotifyConnected = False
    form = None
    if request.user.emailYM != (None or '') and request.user.passwordYM != (None or ''):
        yandexMusicConnected = True
    if request.user.clientIdSP != (None or '') :
        spotifyConnected = True
    if request.user.is_authenticated:
        form = yearSortForm(request.user)
        authenticated = True
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
    else:
        authenticated = False
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'

    tag = Tag.objects.get(id=id)
    albums = Album.objects.filter(album_users=request.user, tags=tag)
    context = {
        'title': 'Playlists',
        'albums': albums,
        'username': username,
        'yandexMusicConnected': yandexMusicConnected,
        'log_message': log_message,
        'log_link': log_link,
        'authenticated': authenticated,
        'spotifyConnected': spotifyConnected,
        'form': form,
    }
    return render(request, 'mainapp/playlists.html', context)

#переход в раздел альбомов по лейблу
def playlistLabels(request, id):
    yandexMusicConnected = False
    spotifyConnected = False
    form = None
    if request.user.emailYM != (None or '') and request.user.passwordYM != (None or ''):
        yandexMusicConnected = True
    if request.user.clientIdSP != (None or '') :
        spotifyConnected = True
    if request.user.is_authenticated:
        form = yearSortForm(request.user)
        authenticated = True
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
    else:
        authenticated = False
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'

    user = request.user
    label = Label.objects.get(id=id)
    albums = Album.objects.filter(album_users=request.user, labels=label)
    context = {
        'title': 'Playlists',
        'albums': albums,
        'username': username,
        'yandexMusicConnected': yandexMusicConnected,
        'spotifyConnected': spotifyConnected,
        'log_message': log_message,
        'log_link': log_link,
        'form': form,
        'authenticated': authenticated,
    }
    return render(request, 'mainapp/playlists.html', context)

#переход в раздел альбомов по жанру
def playlistGenres(request, id):
    yandexMusicConnected = False
    spotifyConnected = False
    form = None
    if request.user.emailYM != (None or '') and request.user.passwordYM != (None or ''):
        yandexMusicConnected = True
    if request.user.clientIdSP != (None or '') :
        spotifyConnected = True
    if request.user.is_authenticated:
        form = yearSortForm(request.user)
        authenticated = True
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
    else:
        authenticated = False
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'

    user = request.user
    genre = Genre.objects.get(id=id)
    albums = Album.objects.filter(album_users=request.user, genres=genre)
    context = {
        'title': 'Playlists',
        'albums': albums,
        'username': username,
        'yandexMusicConnected': yandexMusicConnected,
        'spotifyConnected': spotifyConnected,
        'log_message': log_message,
        'log_link': log_link,
        'form': form,
        'authenticated': authenticated,
    }
    return render(request, 'mainapp/playlists.html', context)

#переход в раздел альбомов по стилю
def playlistStyles(request, id):
    yandexMusicConnected = False
    spotifyConnected = False
    form = None
    if request.user.emailYM != (None or '') and request.user.passwordYM != (None or ''):
        yandexMusicConnected = True
    if request.user.clientIdSP != (None or '') :
        spotifyConnected = True
    if request.user.is_authenticated:
        authenticated = True
        form = yearSortForm(request.user)
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
    else:
        authenticated = False
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'

    user = request.user
    style = Style.objects.get(id=id)
    albums = Album.objects.filter(album_users=request.user, styles=style)
    context = {
        'title': 'Playlists',
        'albums': albums,
        'username': username,
        'form': form,
        'yandexMusicConnected': yandexMusicConnected,
        'spotifyConnected': spotifyConnected,
        'log_message': log_message,
        'log_link': log_link,
        'authenticated': authenticated,
    }
    return render(request, 'mainapp/playlists.html', context)

#переход в раздел альбомов по источнику (Яндекс Музыка или Spotify)
def playlistSource(request, id):
    form = None
    yandexMusicConnected = False
    spotifyConnected = False
    source = 0
    if id == 1:
        source = 'YM'
    if id == 2:
        source = 'SP'
    albums = request.user.albums.filter(source=source)
    if request.user.emailYM != (None or '') and request.user.passwordYM != (None or ''):
        yandexMusicConnected = True
    if request.user.clientIdSP != (None or '') :
        spotifyConnected = True
    if request.user.is_authenticated:
        form = yearSortForm(request.user)
        authenticated = True
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
    else:
        authenticated = False
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'
    context = {
        'title': 'Playlists',
        'albums': albums,
        'username': username,
        'form': form,
        'yandexMusicConnected': yandexMusicConnected,
        'spotifyConnected': spotifyConnected,
        'log_message': log_message,
        'log_link': log_link,
        'authenticated': authenticated,
    }
    return render(request, 'mainapp/playlists.html', context)

#переход в раздел альбомов по артисту
def playlistArtists(request, id):
    form = None
    yandexMusicConnected = False
    spotifyConnected = False
    if request.user.emailYM != (None or '') and request.user.passwordYM != (None or ''):
        yandexMusicConnected = True
    if request.user.clientIdSP != (None or '') :
        spotifyConnected = True
    if request.user.is_authenticated:
        form = yearSortForm(request.user)
        authenticated = True
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
    else:
        authenticated = False
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'

    user = request.user
    artist = Artist.objects.get(id=id)
    albums = Album.objects.filter(album_users=request.user, artists=artist)
    context = {
        'title': 'Playlists',
        'albums': albums,
        'username': username,
        'form': form,
        'yandexMusicConnected': yandexMusicConnected,
        'spotifyConnected': spotifyConnected,
        'log_message': log_message,
        'log_link': log_link,
        'authenticated': authenticated,
    }
    return render(request, 'mainapp/playlists.html', context)

#переход в раздел альбомов по году
def playlistYears(request, year):
    yandexMusicConnected = False
    form = None
    spotifyConnected = False
    if request.user.emailYM != (None or '') and request.user.passwordYM != (None or ''):
        yandexMusicConnected = True
    if request.user.clientIdSP != (None or '') :
        spotifyConnected = True
    if request.user.is_authenticated:
        form = yearSortForm(request.user)
        authenticated = True
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
    else:
        authenticated = False
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'

    albums = Album.objects.filter(album_users=request.user, year=year)
    context = {
        'title': 'Playlists',
        'albums': albums,
        'form': form,
        'username': username,
        'yandexMusicConnected': yandexMusicConnected,
        'spotifyConnected': spotifyConnected,
        'log_message': log_message,
        'log_link': log_link,
        'authenticated': authenticated,
    }
    return render(request, 'mainapp/playlists.html', context)

def deleteTagRequest(request, pk):
    tagRequest = TagShareRequest.objects.get(pk=pk)
    if tagRequest != None:
        tagRequest.delete()
    return HttpResponseRedirect('/friends/')

class tagShareRequestClass:
    pk = 0
    user_to = None
    user_from = None
    tags = []
    def __init__(self, user_to_pk, user_from_pk, tags, pk):
        self.user_to = SiteUser.objects.get(pk=user_to_pk)
        self.user_from = SiteUser.objects.get(pk=user_from_pk)
        self.tags = tags
        self.pk = pk

def acceptTags(request, id):
    print("ACCEPT TAGS!!!")
    reqTags = TagShareRequest.objects.get(pk=id)
    if reqTags != None:
        tags = reqTags.tags
        user_to = SiteUser.objects.get(id=reqTags.user_to_pk)
        user_from = SiteUser.objects.get(id=reqTags.user_from_pk)
        for t in tags.all():
            print("ACCEPT 1")
            albums = Album.objects.all().filter(album_users=user_from)
            albums = albums.filter(tags=t)
            print(albums)
            for al in albums.all():
                try:
                    tag = Tag.objects.get(name=t.name, user_pk=reqTags.user_to_pk, user_from_pk=reqTags.user_from_pk)
                except:
                    tag = Tag(name=t.name, user_pk=reqTags.user_to_pk, user_from_pk=reqTags.user_from_pk)
                    tag.save()
                if tag not in list(al.tags.all()):
                    al.tags.add(tag)
                    al.save()
                if al not in list(user_to.albums.all()):
                    user_to.albums.add(al)
                album_another = None
                if al.idYandex == 0:
                    try:
                        album_another = user_to.albums.get(idDiscogs=al.idDiscogs, idSpotify='-1')
                    except:
                        album_another = None
                if al.idSpotify == '-1':
                    try:
                        album_another = user_to.albums.get(idDiscogs=al.idDiscogs, idYandex=0)
                    except:
                        album_another = None
                if album_another != None:
                    if tag not in list(album_another.tags.all()):
                        album_another.tags.add(tag)
                        album_another.save()
        reqTags.delete()
    return HttpResponseRedirect('/friends/')

def friends(request):
    friendRequests = []
    friends_found = []
    outgoingRequests = []
    unacceptedRequests = []
    tagShareRequestsUnaccepted = []
    tagShareRequestsSent = []
    createdTags = []
    if request.user.is_authenticated:
        authenticated = True
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
        friends = request.user.friends.all()
        tagShareReqUnaccepted = TagShareRequest.objects.filter(user_to_pk=request.user.pk)
        tagShareReqSent = TagShareRequest.objects.filter(user_from_pk=request.user.pk)
        unacceptedRequests = FriendRequest.objects.all().filter(user_to=request.user)
        createdTags = Tag.objects.filter(user_pk=request.user.pk, user_from_pk=request.user.pk)

        for req in tagShareReqUnaccepted:
            tagShareRequestsUnaccepted.append(tagShareRequestClass(user_to_pk=req.user_to_pk, user_from_pk=req.user_from_pk, tags=req.tags.all(), pk=req.pk))
        for req in tagShareReqSent:
            tagShareRequestsSent.append(tagShareRequestClass(user_to_pk=req.user_to_pk, user_from_pk=req.user_from_pk, tags=req.tags.all(), pk=req.pk))
        if request.method == "POST":
            form = friendRequestForm(request.POST)
            if form.is_valid():
                friends_username = form.cleaned_data['friend_name']
                friends_found = SiteUser.objects.all().filter(username__contains=friends_username).exclude(username=request.user.username).exclude(friend_to=request.user)
                if len(friends_found) > 5:
                    friends_found = friends_found[:5]
        else:
            form = friendRequestForm()
        outgoingRequests = FriendRequest.objects.all().filter(user_from=request.user)
        friendReq = FriendRequest.objects.all().filter(user_to=request.user)
        for i in range(0, len(friendReq)):
            friendRequests.append(friendReq[i])

    else:
        authenticated = False
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'
        friends = []
        form = None
    context = {
        'authenticated': authenticated,
        'log_message': log_message,
        'log_link': log_link,
        'username': username,
        'friends_found': friends_found,
        'form': form,
        'friendRequests': friendRequests,
        'friends': friends,
        'tagShareRequestsSent': tagShareRequestsSent,
        'tagShareRequestsUnaccepted': tagShareRequestsUnaccepted,
        'unacceptedRequests': unacceptedRequests,
        'outgoingRequests': outgoingRequests,
        'createdTags': createdTags,
    }
    return render(request, 'mainapp/friends.html', context)

def article1(request):
    if request.user.is_authenticated:
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
        authenticated = True
    else:
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'
        authenticated = False
    context = {
        'title': '#1: How can I connect my accounts?',
        'username': username,
        'log_message': log_message,
        'log_link': log_link,
        'authenticated': authenticated,
    }
    return render(request, 'mainapp/article1.html', context)

def article2(request):
    if request.user.is_authenticated:
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
        authenticated = True
    else:
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'
        authenticated = False
    context = {
        'title': '#2: How can I share tags with friends?',
        'username': username,
        'log_message': log_message,
        'log_link': log_link,
        'authenticated': authenticated,
    }
    return render(request, 'mainapp/article2.html', context)

def article3(request):
    if request.user.is_authenticated:
        username = request.user.username
        log_link = 'auth:logout'
        log_message = 'Log out'
        authenticated = True
    else:
        username = ''
        log_link = 'auth:login'
        log_message = 'Log in'
        authenticated = False
    context = {
        'title': '#3: Registration problems',
        'username': username,
        'log_message': log_message,
        'log_link': log_link,
        'authenticated': authenticated,
    }
    return render(request, 'mainapp/article3.html', context)