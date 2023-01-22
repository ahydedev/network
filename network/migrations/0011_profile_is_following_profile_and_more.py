# Generated by Django 4.1.2 on 2022-11-15 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0010_remove_profile_following_remove_profile_followers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_following_profile',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_profile_owner',
            field=models.BooleanField(default=False),
        ),
    ]