# Generated by Django 3.2.6 on 2021-11-20 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_admin', '0013_auto_20211119_0828'),
    ]

    operations = [
        migrations.AddField(
            model_name='sign_in_by_user',
            name='good_day_logs',
            field=models.ManyToManyField(blank=True, related_name='logs_good_day', to='site_admin.User_Log'),
        ),
    ]