import wikipedia
import requests
import discogs_api as discogs
import authapp.secret as secret
from PIL import Image
import urllib.request
from bs4 import BeautifulSoup
import json
import re
from bs4 import BeautifulSoup
import requests

def get_info(album, artists):
    wikipedia.set_lang('ru')
    if "(Remastered)" in album:
        album = album.replace("(Remastered)", '')
    print('Album:', album)
    print('Artists: ', *artists)
    d = discogs.Client('musicSort/0.1', user_token=secret.user_token)
    genres = []
    styles = []
    year = 0
    labels = set([])
    idDiscogs = 0
    searching = True
    artists_right = []
    for artist, idArtist in artists:
        try:
            art = d.search(artist, type='artist')[0]
            discogs_id = art.id
        except:
            discogs_id = 0
        print("ARTIST DISCOGS ID: ", discogs_id)
        print("CREDITS: ", album, artist, idArtist)
        releases = []
        try:
            releases = d.search(album, artist=artist, type='release')
            if len(releases) == 0:
                try:
                    page = wikipedia.page(artist)
                    url = page.url
                    print(url)
                    req = requests.get(url)
                    soup = BeautifulSoup(req.content, 'html.parser')
                    d = soup.find("div", class_="mw-parser-output")
                    a = d.find("a", title=re.compile("[а-яА-Я] язык"))
                    span = a.findNext('span')
                    print(str(span).split('>')[1].split('<')[0])
                    artist_name = str(span).split('>')[1].split('<')[0]
                    artists_right.append((artist_name, idArtist, discogs_id))
                    print(artist_name)
                    print(artists_right)
                    releases = d.search(album, artist=artists_right, type='release')
                    # print(soup.prettify())
                except:
                    artists_right.append((artist, idArtist, discogs_id))
            else:
                artists_right.append((artist, idArtist, discogs_id))
        except:
            artists_right.append((artist, idArtist, discogs_id))
        if searching == True:
            if len(releases) != 0:
                correct_albums = []
                for i in releases:
                    title = i.title.split("- ")[1]
                    while title[0] == ' ':
                        title = title[1:]
                    while title[-1] == ' ':
                        title = title[:-1]
                    if title.upper() == album.upper() or title.upper() in album.upper() or album.upper() in title.upper():
                        correct_albums.append(i)
                    if len(correct_albums) > 20:
                        break
                correct_albums.sort(key=lambda x: int(x.year))
                for l in correct_albums:
                    print(l.year)
                rignt_index = 0
                for al in range(0, len(correct_albums)):
                    if correct_albums[al].year != 0:
                        rignt_index = al
                        break
                i = correct_albums[rignt_index]
                idDiscogs = i.id
                genres = i.genres
                styles = i.styles
                year = i.year
                labelNames = i.data["labels"]
                for l in labelNames:
                    label_pair = (l['name'], l['id'])
                    print(label_pair)
                    labels.add(label_pair)
                print("Year: ", year)
                try:
                    print("Genres: ", ', '.join(genres))
                except:
                    print("Genres: No information")
                try:
                    print("Styles: ", ', '.join(styles))
                except:
                    print("Styles: No information")
                try:
                    print('Labels: ', end='')
                    for l, idLabel in labels:
                        print(l, end=', ')

                except:
                    print("Labels: No information")
                searching = False
                break
    print('\n')
    return artists_right, year, genres, styles, labels, idDiscogs
# /Users/IS2012/Desktop/projectLIT2021/venv/lib/python3.7/site-packages/wikipedia