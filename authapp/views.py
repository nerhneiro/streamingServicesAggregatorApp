from django.shortcuts import render, HttpResponseRedirect
from authapp.forms import SiteUserLoginForm, SiteUserRegisterForm, SiteUserEditForm, ConnectYandexMusicAccount, ConnectSpotifyAccount, ConnectTokenSpotify
from django.contrib import auth
from django.urls import reverse
from yandex_music.client import Client
import authapp.requestsYandexDiscogs as ryd
from mainapp.models import Album, Artist, Label, Tag, Genre, Style
import time
import authapp.secret as secret
import webbrowser
from urllib.request import urlopen
from PIL import Image
import requests, base64
from urllib.parse import urlencode, quote_plus
from pathlib import Path
from django.core.files import File
from tempfile import NamedTemporaryFile

SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''
SPOTIFY_REDIRECT_URI = ''
SPOTIFY_CODE = ''
def login(request):
    title = 'вход'

    login_form = SiteUserLoginForm(data=request.POST or None)
    if request.method == 'POST' and login_form.is_valid():
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('mainapp:main'))

    content = {'title': title, 'login_form': login_form}
    return render(request, 'authapp/login.html', content)


def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return HttpResponseRedirect(reverse('mainapp:main'))
    else:
        title = 'вход'

        login_form = SiteUserLoginForm(data=request.POST or None)
        if request.method == 'POST' and login_form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                auth.login(request, user)
                # albums = user.albums.all()
                # print(albums)
                return HttpResponseRedirect(reverse('mainapp:main'))

        content = {'title': title, 'login_form': login_form}
        return render(request, 'authapp/login.html', content)


def register(request):
    title = 'регистрация'

    if request.method == 'POST':
        register_form = SiteUserRegisterForm(request.POST, request.FILES)

        if register_form.is_valid():
            register_form.save()
            return HttpResponseRedirect(reverse('auth:login'))
    else:
        register_form = SiteUserRegisterForm()

    content = {'title': title, 'register_form': register_form}

    return render(request, 'authapp/register.html', content)


def edit(request):
    title = 'редактирование'
    edit_form = None
    if request.user.is_authenticated:
        authenticated = True
        if request.method == 'POST':
            edit_form = SiteUserEditForm(request.POST, request.FILES, instance=request.user)
            if edit_form.is_valid():
                edit_form.save()
                return HttpResponseRedirect(reverse('mainapp:account'))
        else:
            edit_form = SiteUserEditForm(instance=request.user)
    else:
        authenticated = False
    content = {'title': title, 'edit_form': edit_form, 'authenticated': authenticated}

    return render(request, 'authapp/edit.html', content)


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
            # print(user.albums.all())
            albumExisting = Album.objects.get(idYandex=int(idYM))
            # print(albumExisting.album_users.all())
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
    for i in user.albums.filter(idSpotify='-1'):
        albumsIdDB.add(i.idYandex)
    albumsRemove1 = albumsIdYM - albumsIdDB
    albumsRemove2 = albumsIdDB - albumsIdYM
    albumsRemove = albumsRemove1.union(albumsRemove2)
    for i in albumsRemove:
        alb = user.albums.get(idYandex=i)
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
    for i in user.albums.filter(idYandex=0):
        albumsIdDB.add(i.idSpotify)
    albumsRemove1 = albumsIdSP - albumsIdDB
    albumsRemove2 = albumsIdDB - albumsIdSP
    albumsRemove = albumsRemove1.union(albumsRemove2)
    for i in albumsRemove:
        alb = user.albums.get(idSpotify=i)
        user.albums.remove(alb)

def removeYM(request):
    albums = request.user.albums.filter(idSpotify='-1')
    for al in albums.all():
        alb = Album.objects.get(idYandex=al.idYandex)
        for t in alb.tags.filter(user_pk=request.user.pk).all():
            alb.tags.remove(t)
            if len(list(Album.objects.filter(album_users=request.user, tags=t).all())) == 0:
                t.delete()
                print("TAG DELETED")
            print("TAG REMOVED")
        request.user.albums.remove(alb)
    request.user.passwordYM = ''
    request.user.emailYM = ''
    request.user.save()
    return HttpResponseRedirect(reverse('mainapp:accounts'))

def removeSpotify(request):
    albums = request.user.albums.filter(idYandex=0)
    for al in albums.all():
        alb = Album.objects.get(idSpotify=al.idSpotify)
        for t in alb.tags.filter(user_pk=request.user.pk).all():
            alb.tags.remove(t)
            if len(list(Album.objects.filter(album_users=request.user, tags=t).all())) == 0:
                t.delete()
                print("TAG DELETED")
            print("TAG REMOVED")
        request.user.albums.remove(alb)
    request.user.passwordSP = ''
    request.user.idSP = ''
    request.user.clientIdSP = ''
    request.user.clientSecretSP = ''
    request.user.tokenAccessSP = ''
    request.user.tokenRefreshSP = ''
    request.user.tokenReserveSP = ''
    request.user.codeSP = ''
    request.user.redirectUriSP = ''
    request.user.emailSP = ''
    request.user.save()
    return HttpResponseRedirect(reverse('mainapp:accounts'))

def connectYM(request):
    title = ''
    message = ''
    password = request.user.passwordYM
    authenticated = request.user.is_authenticated
    # нужна проверка, что еще не указан аккаунт ЯМ. Если он уже есть, нужно выводить предупреждение, что он будет изменен
    # нужна проверка на существование аккаунта
    if request.method == 'POST':
        edit_form = ConnectYandexMusicAccount(request.POST, request.FILES, instance=request.user)
        if edit_form.is_valid():
            user = request.user
            user.passwordYM = secret.hash(edit_form.cleaned_data.get('passwordYM'))
            password = edit_form.cleaned_data.get('passwordYM')
            edit_form.save()
            print("USER PASSWORD: ", user.passwordYM)
            client = Client.from_credentials(edit_form.cleaned_data.get('emailYM'),
                                             edit_form.cleaned_data.get('passwordYM'))
            albums = client.users_likes_albums()
            try:
                fillInDBYandexMusic(albums, request.user)
            except:
                print("TOO MANY REQUESTS ERROR")
                time.sleep(5)
                fillInDBYandexMusic(albums, request.user)
            return HttpResponseRedirect(reverse('mainapp:main'))
    else:
        request.user.passwordYM = secret.hash(password)
        print("HERE PASSWORD", request.user.passwordYM)
        edit_form = ConnectYandexMusicAccount(instance=request.user)
        print("HERE PASSWORD 2", request.user.passwordYM)

    content = {
        'title': title,
        'edit_form': edit_form,
        'message': message,
        'authenticated': authenticated
    }

    return render(request, 'authapp/connectYM.html', content)

def get_albums(token):
    print("GETTING ALBUMS")
    url = 'https://api.spotify.com/v1/me/albums'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    r = requests.get(url, headers=headers)
    print(r)
    response = r.json()
    return response

def refresh(refresh_token, base_64):
    query = "https://accounts.spotify.com/api/token"

    response = requests.post(query,
                             data={"grant_type": "refresh_token",
                                   "refresh_token": refresh_token},
                             headers={"Authorization": "Basic " + base_64})

    response_json = response.json()
    print("REFRESH RESPONSE: ", response_json)

    return response_json["access_token"]

def connectSpotify(request):
    global SPOTIFY_REDIRECT_URI
    global SPOTIFY_CLIENT_ID
    global SPOTIFY_CLIENT_SECRET
    title = ''
    message = ''
    if request.method == 'POST':
        edit_form = ConnectSpotifyAccount(request.POST, request.FILES, instance=request.user)
        if edit_form.is_valid():
            user = request.user
            SPOTIFY_CLIENT_SECRET = secret.hash(edit_form.cleaned_data.get('clientSecretSP'))
            SPOTIFY_CLIENT_ID = edit_form.cleaned_data.get('clientIdSP')
            SPOTIFY_REDIRECT_URI = edit_form.cleaned_data.get('redirectUriSP')
            # edit_form.save()
            return HttpResponseRedirect(reverse('auth:connectTokenSP'))
    else:
        edit_form = ConnectSpotifyAccount(instance=request.user)
    content = {
        'title': title,
        'edit_form': edit_form,
        'message': message,
        'user': request.user,
    }

    return render(request, 'authapp/connectSP.html', content)

def connectTokenSP(request):
    global SPOTIFY_REDIRECT_URI
    global SPOTIFY_CLIENT_ID
    global SPOTIFY_CLIENT_SECRET
    global SPOTIFY_CODE
    user = request.user
    if request.method == 'POST':
        edit_form = ConnectTokenSpotify(request.POST, request.FILES, instance=request.user)
        if edit_form.is_valid():
            user = request.user
            client_id = SPOTIFY_CLIENT_ID
            client_secret = secret.dehash(SPOTIFY_CLIENT_SECRET)
            print("CLIENT SECRET: ", client_secret)
            response_type = 'code'
            redirect_uri = SPOTIFY_REDIRECT_URI
            redirect_uri_encoded = quote_plus(redirect_uri)
            try:
                SPOTIFY_CODE = edit_form.cleaned_data.get('codeSP').split('code=')[1]
            except:
                SPOTIFY_CODE = ''
            body = {
                'grant_type': 'authorization_code',
                'code': SPOTIFY_CODE,
                'redirect_uri': redirect_uri
            }
            client_creds = f"{client_id}:{client_secret}"
            client_creds_64 = base64.b64encode(client_creds.encode())
            header = {
                'Authorization': f'Basic {client_creds_64.decode()}'
            }
            url = 'https://accounts.spotify.com/api/token'
            r = requests.post(url, headers=header, data=body)
            try:
                print("RESPONSE: ", r)
                print("RESPONSE JSON 1: ", r.json())
                response_json = r.json()
                user.tokenAccessSP = response_json['access_token']
                user.tokenRefreshSP = response_json['refresh_token']
                print("ACCESS TOKEN: ",  response_json['access_token'])
                user.clientIdSP = SPOTIFY_CLIENT_ID
                print("USER CLIENT ID: ", user.clientIdSP)
                user.clientSecretSP = SPOTIFY_CLIENT_SECRET
                user.redirectUriSP = SPOTIFY_REDIRECT_URI
                user.codeSP = secret.hash(SPOTIFY_CODE)
                user.save()
            except:
                print("WRONG DATA")
                return HttpResponseRedirect(reverse('auth:connectSpotify'))
            # 'token_type': 'Bearer'
            # 'expires_in': 3600
            # 'scope': 'user-library-read'
            edit_form.save()
            albums = []
            try:
                albums = get_albums(user.tokenAccessSP)['items']
            except:
                try:
                    user.tokenAccessSP = refresh(user.tokenRefreshSP, client_creds_64.decode())
                    albums = get_albums(user.tokenAccessSP)['items']
                except:
                    print("COULDN'T REFRESH AN ACCESS TOKEN")
            print("READY TO FILL IN DB")
            fillInDBSpotify(albums, user)

            return HttpResponseRedirect(reverse('mainapp:main'))
    else:
        print("CONNECT client id: ", SPOTIFY_CLIENT_ID)
        print("CONNECT user client id: ", user.clientIdSP)
        edit_form = ConnectTokenSpotify(instance=request.user)
        client_id = SPOTIFY_CLIENT_ID
        client_secret = secret.dehash(SPOTIFY_CLIENT_SECRET)
        response_type = 'code'
        redirect_uri = SPOTIFY_REDIRECT_URI
        redirect_uri_encoded = quote_plus(redirect_uri)
        token_url = f'https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri_encoded}&scope=user-library-read'
        webbrowser.open(token_url, new=1)
    content = {
        'edit_form': edit_form,
        'user': request.user,
    }
    return render(request, 'authapp/tokenSP.html', content)