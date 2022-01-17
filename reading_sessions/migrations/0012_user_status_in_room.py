# Generated by Django 3.2.6 on 2021-10-27 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('site_admin', '0006_student_progress_last_assessed'),
        ('reading_sessions', '0011_auto_20211027_0845'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_status',
            name='in_room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='status_location', to='site_admin.room'),
        ),
    ]