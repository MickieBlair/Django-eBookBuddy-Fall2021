# Generated by Django 3.2.7 on 2021-10-02 11:44

from django.db import migrations, models
import django.db.models.deletion
import site_admin.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance_Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Attendance Status',
                'verbose_name_plural': 'Attendance Statuses',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Daily_Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, max_length=255)),
                ('date', models.DateField(blank=True, null=True, verbose_name='Date')),
                ('week', models.IntegerField(default=0)),
                ('session_complete', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('archive_session', models.BooleanField(default=False, verbose_name='Archived')),
                ('session_start_date_time', models.DateTimeField(blank=True, null=True, verbose_name='Start Date/Time')),
                ('session_end_date_time', models.DateTimeField(blank=True, null=True, verbose_name='Start Date/Time')),
                ('entry_allowed_start', models.DateTimeField(blank=True, null=True)),
                ('entry_allowed_end', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Session',
                'verbose_name_plural': 'Sessions',
                'ordering': ['date', 'day_time'],
            },
        ),
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('span_name', models.CharField(blank=True, max_length=100)),
                ('number', models.IntegerField(blank=True, null=True)),
                ('short_name', models.CharField(blank=True, max_length=3, null=True)),
                ('letter', models.CharField(blank=True, max_length=3, null=True)),
            ],
            options={
                'verbose_name': 'Day',
                'verbose_name_plural': 'Days',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Day_With_Daily_Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True, verbose_name='Date')),
                ('week', models.IntegerField(default=0)),
                ('count', models.IntegerField(default=0)),
                ('all_complete', models.BooleanField(default=False)),
                ('total_matches', models.IntegerField(default=0)),
                ('total_active_scheduled', models.IntegerField(default=0)),
                ('total_temporary', models.IntegerField(default=0)),
                ('total_complete_scheduled_matches', models.IntegerField(default=0)),
                ('percent_successful', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('total_complete_reading_count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Day With Daily Sessions',
                'verbose_name_plural': 'Days With Daily Sessions',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Day_With_Orientation_Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True, verbose_name='Date')),
                ('time_start', models.TimeField(blank=True, null=True)),
                ('time_end', models.TimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Day With Orientation Meeting',
                'verbose_name_plural': 'Day With Orientation Meetings',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Day_With_Team_Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True, verbose_name='Date')),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Day With Team Meeting',
                'verbose_name_plural': 'Day With Team Meetings',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('span', models.CharField(blank=True, max_length=100, null=True)),
                ('letter', models.CharField(blank=True, max_length=1, null=True)),
            ],
            options={
                'verbose_name': 'Gender',
                'verbose_name_plural': 'Genders',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('short_name', models.CharField(blank=True, max_length=100, null=True)),
                ('letter', models.CharField(blank=True, max_length=1, null=True)),
            ],
            options={
                'verbose_name': 'Grade',
                'verbose_name_plural': 'Grades',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Language',
                'verbose_name_plural': 'Languages',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Mega_Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Mega Team',
                'verbose_name_plural': 'Mega Teams',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True, max_length=2000, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Note',
                'verbose_name_plural': 'Notes',
            },
        ),
        migrations.CreateModel(
            name='Note_Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Note Category',
                'verbose_name_plural': 'Note Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Note_Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Note Group',
                'verbose_name_plural': 'Note Groups',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Reading_Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Reading Level',
                'verbose_name_plural': 'Reading Levels',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('number', models.IntegerField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('room_url', models.URLField(blank=True, max_length=500, null=True)),
                ('occupied', models.BooleanField(default=False)),
                ('num_participants', models.IntegerField(default=0, verbose_name='Count')),
                ('jitsi_num_participants', models.IntegerField(default=0, verbose_name='Jitsi Count')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Room',
                'verbose_name_plural': 'Rooms',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Room_Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('letter', models.CharField(blank=True, max_length=1)),
            ],
            options={
                'verbose_name': 'Room Type',
                'verbose_name_plural': 'Room Types',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'School',
                'verbose_name_plural': 'Schools',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('active_semester', models.BooleanField(default=False)),
                ('full_dates', models.CharField(blank=True, max_length=100, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Semester',
                'verbose_name_plural': 'Semesters',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Server_Time',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('offset', models.IntegerField(blank=True, help_text='-240 DST, -300 no DST', null=True)),
                ('active', models.BooleanField(default=True)),
                ('entry_allowed_start', models.TimeField(blank=True, null=True)),
                ('entry_allowed_end', models.TimeField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Server Time',
                'verbose_name_plural': 'Server Times',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Session_Day_Time',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_start', models.TimeField()),
                ('time_end', models.TimeField()),
                ('session_slot', models.CharField(max_length=1)),
                ('currently_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Session Day/Time',
                'verbose_name_plural': 'Session Days/Times',
                'ordering': ['day__number', 'session_slot'],
            },
        ),
        migrations.CreateModel(
            name='Session_Reading_Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Session Reading Level Assessment',
                'verbose_name_plural': 'Session Reading Level Assessments',
                'ordering': ['user', 'session__date', 'session__day_time'],
            },
        ),
        migrations.CreateModel(
            name='Sign_In_By_Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled', models.BooleanField(default=False)),
                ('signed_in', models.BooleanField(default=False)),
                ('excused', models.BooleanField(default=False)),
                ('meet_with_sheduled', models.BooleanField(default=False)),
                ('temp_match_created', models.BooleanField(default=False)),
                ('total_sign_ins', models.IntegerField(blank=True, null=True)),
                ('pending_minutes', models.IntegerField(blank=True, default=0, null=True)),
                ('breakout_minutes', models.IntegerField(blank=True, default=0, null=True)),
                ('meeting_minutes', models.IntegerField(blank=True, default=0, null=True)),
                ('total_minutes', models.IntegerField(blank=True, default=0, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'User Sign In By Day',
                'verbose_name_plural': 'User Sign Ins By Day',
                'ordering': ['user__full_name', 'day__date'],
            },
        ),
        migrations.CreateModel(
            name='Site_View_Error',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.CharField(blank=True, max_length=255, null=True)),
                ('view', models.CharField(blank=True, max_length=255, null=True)),
                ('location_in_view', models.CharField(blank=True, max_length=255, null=True)),
                ('occurred_for_user', models.CharField(blank=True, max_length=255, null=True)),
                ('error_text', models.TextField(blank=True, max_length=2000, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
            ],
            options={
                'verbose_name': 'Site View Error',
                'verbose_name_plural': 'Site View Errors',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Staff_Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_number', models.CharField(blank=True, max_length=255, null=True)),
                ('comment', models.TextField(blank=True, max_length=1000, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=site_admin.models.image_upload_location, verbose_name='Photo')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Staff Profile',
                'verbose_name_plural': 'Staff Profiles',
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='Student_Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_needed', models.BooleanField(default=False)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('contact_person', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_relationship', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=255, null=True)),
                ('comment', models.TextField(blank=True, max_length=1000, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=site_admin.models.image_upload_location, verbose_name='Photo')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Student Profile',
                'verbose_name_plural': 'Student Profiles',
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='Student_Progress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Student Progress',
                'verbose_name_plural': 'Student Progress',
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='Student_Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_logs', models.BooleanField(default=True)),
                ('total_sign_ins', models.IntegerField(blank=True, null=True)),
                ('has_active_match', models.BooleanField(default=False)),
                ('total_active_matches', models.IntegerField(blank=True, null=True)),
                ('total_inactive_matches', models.IntegerField(blank=True, null=True)),
                ('total_scheduled_sessions', models.IntegerField(blank=True, null=True)),
                ('scheduled_semester_hours', models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=10, null=True)),
                ('total_semester_hours', models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=10, null=True)),
                ('semester_pending_hours', models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=10, null=True)),
                ('semester_breakout_hours', models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=10, null=True)),
                ('scheduled_count', models.IntegerField(blank=True, null=True)),
                ('attended_count', models.IntegerField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('note', models.TextField(blank=True, max_length=1000, null=True)),
                ('total_temp_matches', models.IntegerField(blank=True, default=0, null=True)),
            ],
            options={
                'verbose_name': 'Student Report',
                'verbose_name_plural': 'Student Reports',
                'ordering': ['user__full_name'],
            },
        ),
        migrations.CreateModel(
            name='System_Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('eng_message', models.TextField(blank=True, max_length=2000, null=True)),
                ('span_message', models.TextField(blank=True, max_length=2000, null=True)),
            ],
            options={
                'verbose_name': 'System Message',
                'verbose_name_plural': 'System Messages',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('meeting_time', models.TimeField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Team',
                'verbose_name_plural': 'Teams',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Team_Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Team Meeting',
                'verbose_name_plural': 'Team Meetings',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Upload_CSV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('csv_file', models.FileField(upload_to='uploads/initial/')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Upload CSV',
                'verbose_name_plural': 'Upload CSVs',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='User_Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('time_in', models.DateTimeField()),
                ('time_out', models.DateTimeField(blank=True, null=True)),
                ('duration_seconds', models.IntegerField(blank=True, null=True, verbose_name='Duration(seconds)')),
                ('logged_in', models.BooleanField(default=False)),
                ('processed', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'User Log',
                'verbose_name_plural': 'User Logs',
            },
        ),
        migrations.CreateModel(
            name='Volunteer_Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_needed', models.BooleanField(default=False)),
                ('in_school', models.BooleanField(default=False)),
                ('highest_completed', models.TextField(blank=True, max_length=1000, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=255, null=True)),
                ('comment', models.TextField(blank=True, max_length=1000, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=site_admin.models.image_upload_location, verbose_name='Photo')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'Volunteer Profile',
                'verbose_name_plural': 'Volunteer Profiles',
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='Volunteer_Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_logs', models.BooleanField(default=True)),
                ('total_sign_ins', models.IntegerField(blank=True, null=True)),
                ('has_active_match', models.BooleanField(default=False)),
                ('total_active_matches', models.IntegerField(blank=True, null=True)),
                ('total_inactive_matches', models.IntegerField(blank=True, null=True)),
                ('total_scheduled_sessions', models.IntegerField(blank=True, null=True)),
                ('total_semester_hours', models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=10, null=True)),
                ('scheduled_count', models.IntegerField(blank=True, null=True)),
                ('attended_count', models.IntegerField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('total_temp_matches', models.IntegerField(blank=True, default=0, null=True)),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_semester_report', to='site_admin.semester')),
                ('sessions_scheduled', models.ManyToManyField(blank=True, related_name='volunteer_scheduled_sessions', to='site_admin.Daily_Session')),
            ],
            options={
                'verbose_name': 'Volunteer Report',
                'verbose_name_plural': 'Volunteer Reports',
                'ordering': ['user__full_name'],
            },
        ),
    ]
