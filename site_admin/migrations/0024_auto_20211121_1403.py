# Generated by Django 3.2.6 on 2021-11-21 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_admin', '0023_auto_20211121_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='server_time',
            name='vol_end',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='server_time',
            name='vol_start',
            field=models.TimeField(blank=True, null=True),
        ),
    ]