# Generated by Django 3.2.6 on 2021-11-18 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_admin', '0007_sign_in_by_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='sign_in_by_user',
            name='missing_out',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sign_in_by_user',
            name='problem_user',
            field=models.BooleanField(default=False),
        ),
    ]
