# Generated by Django 3.2.6 on 2021-10-08 12:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reading_sessions', '0005_user_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user_status',
            options={'ordering': ['user'], 'verbose_name': 'A_User_Status', 'verbose_name_plural': 'A_User_Status'},
        ),
    ]
