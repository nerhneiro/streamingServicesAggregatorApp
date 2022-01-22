from django import forms
from mainapp.models import Genre, Style, Label, Album, Tag, Artist
from authapp.models import SiteUser
#добавить привязку к user'у


class friendRequestForm(forms.Form):
    friend_name = forms.CharField(label="Username", max_length=128)

class friendRequestConfirmForm(forms.Form):
    friend_name = forms.CharField(label="Username", max_length=128)

class shareTagsForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(queryset=None, label='tags', required=False)
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'search_all' and field_name != 'year':
                field.widget.attrs['class'] = 'form_sort_choice'
            if field_name == 'year':
                field.widget.attrs['class'] = 'form_sort_year_choice'
        if user.is_anonymous == False:
            self.fields['tags'].queryset = Tag.objects.filter(user_pk=user.pk, user_from_pk=user.pk)
            self.fields['tags'].label_from_instance = lambda obj: "%s" % obj.name

class addTagForm(forms.Form):
    tag_name = forms.CharField(label='Name', max_length=128)

class yearSortForm(forms.Form):
    year = forms.IntegerField(label='Year', max_value=2021, min_value=1500, required=False)
    search_all = forms.BooleanField(label='All the fields required', required=False)
    genres = forms.ModelMultipleChoiceField(queryset=None, required=False)
    styles = forms.ModelMultipleChoiceField(queryset=None, required=False)
    labels = forms.ModelMultipleChoiceField(queryset=None, required=False)
    tags = forms.ModelMultipleChoiceField(queryset=None, required=False)
    users_tags = forms.MultipleChoiceField(choices=(), required=False)
    artists = forms.ModelMultipleChoiceField(queryset=None, required=False)
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'search_all' and field_name != 'year':
                field.widget.attrs['class'] = 'form_sort_choice'
            if field_name == 'year':
                field.widget.attrs['class'] = 'form_sort_year_choice'
        print("USER: ", user)
        if user.is_anonymous == False:
            self.fields['genres'].queryset = Genre.objects.filter(genred_albums__album_users=user).distinct()
            self.fields['genres'].label_from_instance = lambda obj: "%s" % obj.name
            self.fields['styles'].queryset = Style.objects.filter(styled_albums__album_users=user).distinct()
            self.fields['styles'].label_from_instance = lambda obj: "%s" % obj.name
            self.fields['labels'].queryset = Label.objects.filter(labeled_albums__album_users=user).distinct()
            ch = set()
            for i in Tag.objects.filter(user_pk=user.pk).exclude(user_from_pk=user.pk).distinct():
                ch.add((i.user_from_pk, SiteUser.objects.get(pk=i.user_from_pk)))
            ch = tuple(ch)
            self.fields['users_tags'].choices = ch
            print("CHOICES: ", self.fields['users_tags'].choices)
            self.fields['labels'].label_from_instance = lambda obj: "%s" % obj.name
            self.fields['tags'].queryset = Tag.objects.filter(user_pk=user.pk)
            self.fields['tags'].label_from_instance = lambda obj: "%s" % obj.name
            self.fields['artists'].queryset = Artist.objects.filter(albums__album_users=user).distinct()
            self.fields['artists'].label_from_instance = lambda obj: "%s" % obj.name
            self.fields['tags'].label_from_instance = lambda obj: "%s" % obj.name