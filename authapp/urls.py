from django.urls import path

import authapp.views as authapp

app_name = 'authapp'

urlpatterns = [
    path('login/', authapp.login, name='login'),
    path('logout/', authapp.logout, name='logout'),
    path('register/', authapp.register, name='register'),
    path('edit/', authapp.edit, name='edit'),
    path('connectYM/', authapp.connectYM, name='connectYM'),
    path('connectSpotify/', authapp.connectSpotify, name='connectSpotify'),
    path('connectTokenSP/', authapp.connectTokenSP, name='connectTokenSP'),
    path('removeSpotify/', authapp.removeSpotify, name='removeSpotify'),
    path('removeYM/', authapp.removeYM, name='removeYM'),
]
