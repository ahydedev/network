# Generated by Django 4.1.2 on 2022-11-16 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0017_remove_like_liked_by_remove_like_post_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='following',
            field=models.IntegerField(blank=True, max_length=3, null=True),
        ),
    ]