# Generated by Django 2.2 on 2021-06-07 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0004_siteuser_friendrequests'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteuser',
            name='codeSP',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Spotify code'),
        ),
    ]