# Generated by Django 3.2.6 on 2021-10-16 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar_img',
            field=models.ImageField(blank=True, null=True, upload_to='avatars'),
        ),
    ]
