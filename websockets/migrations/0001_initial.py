# Generated by Django 3.2.7 on 2021-10-02 11:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('site_admin', '0002_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Jitsi_Chat_Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ('date_created', models.DateField(auto_now_add=True, verbose_name='date created')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Jitsi Chat Room',
                'verbose_name_plural': 'Jitsi Chat Rooms',
            },
        ),
        migrations.CreateModel(
            name='Jitsi_Room_Chat_Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('display', models.BooleanField(default=True)),
                ('meeting_room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jitsi_room_messages', to='site_admin.room')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='websockets.jitsi_chat_room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Jitsi Chat Room Message',
                'verbose_name_plural': 'Jitsi Chat Room Messages',
            },
        ),
        migrations.CreateModel(
            name='PrivateChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('last_use', models.DateTimeField()),
                ('connected_users', models.ManyToManyField(blank=True, related_name='connected_users', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(blank=True, related_name='room_members', to=settings.AUTH_USER_MODEL)),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user1', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user2', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Private Chat Room',
                'verbose_name_plural': 'Private Chat Rooms',
            },
        ),
        migrations.CreateModel(
            name='Room_Chat_Error',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.CharField(blank=True, max_length=255, null=True)),
                ('function_name', models.CharField(blank=True, max_length=255, null=True)),
                ('location_in_function', models.CharField(blank=True, max_length=255, null=True)),
                ('occurred_for_user', models.CharField(blank=True, max_length=255, null=True)),
                ('error_text', models.TextField(blank=True, max_length=2000, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
            ],
            options={
                'verbose_name': 'Room Chat Error',
                'verbose_name_plural': 'Room Chat Errors',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='RoomChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='msg_sender', to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='websockets.privatechatroom')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='msg_recipient', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Private Chat Room Message',
                'verbose_name_plural': 'Private Chat Room Messages',
            },
        ),
        migrations.CreateModel(
            name='Staff_Chat_Error',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.CharField(blank=True, max_length=255, null=True)),
                ('function_name', models.CharField(blank=True, max_length=255, null=True)),
                ('location_in_function', models.CharField(blank=True, max_length=255, null=True)),
                ('occurred_for_user', models.CharField(blank=True, max_length=255, null=True)),
                ('error_text', models.TextField(blank=True, max_length=2000, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
            ],
            options={
                'verbose_name': 'Staff Chat Error',
                'verbose_name_plural': 'Staff Chat Errors',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Staff_Chat_Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ('date_created', models.DateField(auto_now_add=True, verbose_name='date created')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Staff Chat Room',
                'verbose_name_plural': 'Staff Chat Rooms',
            },
        ),
        migrations.CreateModel(
            name='Websocket_Error',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.CharField(blank=True, max_length=255, null=True)),
                ('function_name', models.CharField(blank=True, max_length=255, null=True)),
                ('location_in_function', models.CharField(blank=True, max_length=255, null=True)),
                ('occurred_for_user', models.CharField(blank=True, max_length=255, null=True)),
                ('error_text', models.TextField(blank=True, max_length=2000, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
            ],
            options={
                'verbose_name': 'Websocket Error',
                'verbose_name_plural': 'Websocket Errors',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='User_Private_Room_List',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_count', models.IntegerField(default=0)),
                ('total_unread_private', models.IntegerField(default=0)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('private_rooms', models.ManyToManyField(blank=True, related_name='private_room_list_rooms', to='websockets.PrivateChatRoom')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='private_room_list', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Private Room List',
                'verbose_name_plural': 'User Private Room List',
            },
        ),
        migrations.CreateModel(
            name='UnreadChatRoomMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0)),
                ('most_recent_message', models.CharField(blank=True, max_length=500, null=True)),
                ('reset_timestamp', models.DateTimeField()),
                ('last_message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last', to='websockets.roomchatmessage')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_unread', to='websockets.privatechatroom')),
                ('unread_msgs', models.ManyToManyField(blank=True, related_name='unread_messages', to='websockets.RoomChatMessage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='private_unread', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Unread Private Chat Message',
                'verbose_name_plural': 'Unread Private Chat Messages',
            },
        ),
        migrations.CreateModel(
            name='Staff_Room_Unread_Chat_Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unread_count', models.IntegerField(default=0, verbose_name='Unread Count')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='room_unread_staff', to='websockets.staff_chat_room')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='unread_staff', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Staff Chat Uread Message',
                'verbose_name_plural': 'Staff Chat Unread Messages',
            },
        ),
        migrations.CreateModel(
            name='Staff_Room_Chat_Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('meeting_room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_messages', to='site_admin.room')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='websockets.staff_chat_room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Staff Chat Room Message',
                'verbose_name_plural': 'Staff Chat Room Messages',
            },
        ),
        migrations.CreateModel(
            name='Socket_Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('count', models.IntegerField(default=0, verbose_name='Count')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('connected_users', models.ManyToManyField(blank=True, related_name='group_connected', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Socket Group',
                'verbose_name_plural': 'Socket Groups',
            },
        ),
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redirect_url', models.URLField(blank=True, max_length=500, null=True)),
                ('auto_send', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_by_user', to=settings.AUTH_USER_MODEL)),
                ('to_room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location', to='site_admin.room')),
                ('to_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='redirect_to', to=settings.AUTH_USER_MODEL)),
                ('user_to_redirect', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='redirect', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Redirect',
                'verbose_name_plural': 'Redirects',
            },
        ),
        migrations.CreateModel(
            name='Private_Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='read at')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('message', models.TextField()),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Private Message',
                'verbose_name_plural': 'Private Messages',
            },
        ),
        migrations.CreateModel(
            name='Private_Conversation_Pair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('user1_has_unread', models.BooleanField(default=True)),
                ('user2_has_unread', models.BooleanField(default=True)),
                ('messages', models.ManyToManyField(blank=True, related_name='pair_messages', to='websockets.Private_Message')),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_1', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_2', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, related_name='pair_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Private Conversation Pair',
                'verbose_name_plural': 'Private Conversation Pairs',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redirect_url', models.URLField(blank=True, help_text='The URL to be visited when a notification is clicked.', max_length=500, null=True)),
                ('verb', models.CharField(blank=True, max_length=255, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('from_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to=settings.AUTH_USER_MODEL)),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
            },
        ),
        migrations.CreateModel(
            name='Jitsi_Room_Unread_Chat_Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unread_count', models.IntegerField(default=0, verbose_name='Unread Count')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('meeting_room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jitsi_messages', to='site_admin.room')),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='room_unread_general', to='websockets.jitsi_room_chat_message')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='unread_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Jitsi Chat Uread Message',
                'verbose_name_plural': 'Jitsi Chat Unread Messages',
            },
        ),
        migrations.CreateModel(
            name='Help_Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_url', models.URLField(blank=True, max_length=500, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
                ('user_message', models.TextField(blank=True)),
                ('done', models.BooleanField(default=False)),
                ('visited_time', models.DateTimeField(blank=True, null=True, verbose_name='visited time')),
                ('from_room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='room_needing_help', to='site_admin.room')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request', to=settings.AUTH_USER_MODEL)),
                ('visited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='completed_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Help Request',
                'verbose_name_plural': 'Help Requests',
            },
        ),
    ]
