from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm

from .models import SiteUser
from yandex_music.client import Client
import authapp.secret as secret
import authapp.requestsYandexDiscogs as ryd

class SiteUserLoginForm(AuthenticationForm):
    class Meta:
        model = SiteUser
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super(SiteUserLoginForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form_signin'


class SiteUserRegisterForm(UserCreationForm):
    class Meta:
        model = SiteUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SiteUserRegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form_register'
            field.help_text = ''
class ConnectSpotifyAccount(UserChangeForm):
    class Meta:
        model = SiteUser
        fields = ('clientIdSP', 'clientSecretSP', 'redirectUriSP')

    def __init__(self, *args, **kwargs):
        super(ConnectSpotifyAccount, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form_register'
            field.help_text = ''

class ConnectTokenSpotify(UserChangeForm):
    class Meta:
        model = SiteUser
        fields = ('codeSP',)

    def __init__(self, *args, **kwargs):
        super(ConnectTokenSpotify, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form_register'
            field.help_text = ''
        self.fields['codeSP'].label_from_instance = 'Code'

class ConnectYandexMusicAccount(UserChangeForm):
    passwordYM = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = SiteUser
        fields = ('emailYM', 'passwordYM')

    def __init__(self, *args, **kwargs):
        super(ConnectYandexMusicAccount, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form_register'
            field.help_text = ''

    def clean_password(self):
        email = self.cleaned_data['emailYM']
        password = self.cleaned_data['passwordYM']
        try:
            client = Client.from_credentials(email, self.cleaned_data['passwordYM'])
        except:
            raise forms.ValidationError("This Yandex Music account doesn't exist!")

class SiteUserEditForm(UserChangeForm):
    class Meta:
        model = SiteUser
        fields = ('username', 'first_name', 'last_name', 'email', 'age')

    def __init__(self, *args, **kwargs):
        super(SiteUserEditForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''

