# Generated by Django 4.1.2 on 2022-11-13 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='likes',
        ),
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.CharField(blank=True, max_length=5),
        ),
    ]
