from django.urls import path

import mainapp.views as mainapp

app_name = 'mainapp'

urlpatterns = [
    path('', mainapp.main, name='main'),
    path('article1', mainapp.article1, name='article1'),
    path('article2', mainapp.article2, name='article2'),
    path('article3', mainapp.article3, name='article3'),
    path('playlists/', mainapp.playlists, name='playlists'),
    path('playlists/<int:pk>/', mainapp.playlist, name='playlist'),
    path('playlistTags/<int:id>', mainapp.playlistTags, name='playlistTags'),
    path('playlistLabels/<int:id>', mainapp.playlistLabels, name='playlistLabels'),
    path('playlistGenres/<int:id>', mainapp.playlistGenres, name='playlistGenres'),
    path('playlistStyles/<int:id>', mainapp.playlistStyles, name='playlistStyles'),
    path('playlistArtists/<int:id>', mainapp.playlistArtists, name='playlistArtists'),
    path('playlistYears/<int:year>', mainapp.playlistYears, name='playlistYears'),
    path('playlistSource/<int:id>', mainapp.playlistSource, name='playlistSource'),
    path('deleteTagRequest/<int:pk>', mainapp.deleteTagRequest, name='deleteTagRequest'),
    path('sendFriendRequest/<int:id>', mainapp.sendFriendRequest, name='sendFriendRequest'),
    path('acceptFriendRequest/<int:id>', mainapp.acceptFriendRequest, name='acceptFriendRequest'),
    path('declineFriendRequest/<int:id>', mainapp.declineFriendRequest, name='declineFriendRequest'),
    path('cancelFriendRequest/<int:id>', mainapp.cancelFriendRequest, name='cancelFriendRequest'),
    path('deleteFriend/<int:id>', mainapp.deleteFriend, name='deleteFriend'),
    path('shareTag/<int:id>', mainapp.shareTag, name='shareTag'),
    path('shareTags/<int:id>', mainapp.shareTags, name='shareTags'),
    path('friends/', mainapp.friends, name='friends'),
    path('accounts/', mainapp.connected, name='accounts'),
    path('account/', mainapp.account, name='account'),
    path('updateDB/', mainapp.updateDB, name='updateDB'),
    path('acceptTags/<int:id>', mainapp.acceptTags, name='acceptTags'),
    path('declineTags/<int:id>', mainapp.declineTags, name='declineTags'),
]