# Generated by Django 3.2.6 on 2021-11-22 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reading_sessions', '0013_auto_20211104_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='a_problem_user',
            name='comment',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
