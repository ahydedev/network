# Generated by Django 4.1.2 on 2022-11-14 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0007_alter_profile_followers_alter_profile_following'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person_posts', to='network.profile'),
        ),
    ]
