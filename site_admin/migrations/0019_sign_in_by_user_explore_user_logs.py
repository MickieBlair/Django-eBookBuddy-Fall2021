# Generated by Django 3.2.6 on 2021-11-20 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_admin', '0018_user_log_needs_attention'),
    ]

    operations = [
        migrations.AddField(
            model_name='sign_in_by_user',
            name='explore_user_logs',
            field=models.BooleanField(default=False),
        ),
    ]
