# Generated by Django 3.2.6 on 2021-10-19 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_admin', '0005_auto_20211019_0646'),
    ]

    operations = [
        migrations.AddField(
            model_name='student_progress',
            name='last_assessed',
            field=models.DateField(blank=True, null=True),
        ),
    ]