# Generated by Django 3.2.6 on 2021-11-20 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_admin', '0014_sign_in_by_user_good_day_logs'),
    ]

    operations = [
        migrations.AddField(
            model_name='sign_in_by_user',
            name='completely_done',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sign_in_by_user',
            name='diff_count',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
