# Generated by Django 3.2.6 on 2021-11-19 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_admin', '0009_auto_20211119_0641'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_log',
            name='during_jitsi_open',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user_log',
            name='time_in_jitsi_open',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user_log',
            name='time_out_jitsi_open',
            field=models.BooleanField(default=False),
        ),
    ]
