# Generated by Django 3.2.6 on 2021-10-12 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jitsi_data', '0002_jitsi_websocket_error'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jitsi_user_status',
            name='time_in',
        ),
        migrations.RemoveField(
            model_name='jitsi_user_status',
            name='time_out',
        ),
        migrations.AddField(
            model_name='jitsi_user_status',
            name='jitsi_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
