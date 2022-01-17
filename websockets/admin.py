from django.contrib import admin
from django.db import models
from django.core.paginator import Paginator
from django.core.cache import cache

from websockets.models import Websocket_Error, Room_Chat_Error, Staff_Chat_Error
from websockets.models import Socket_Group
from websockets.models import Notification
from websockets.models import Redirect
from websockets.models import Help_Request

from websockets.models import Jitsi_Chat_Room, Jitsi_Room_Chat_Message
from websockets.models import Staff_Chat_Room, Staff_Room_Chat_Message

from websockets.models import PrivateChatRoom, RoomChatMessage, UnreadChatRoomMessages
from websockets.models import Staff_Room_Unread_Chat_Message
from websockets.models import Jitsi_Room_Unread_Chat_Message
from websockets.models import Private_Message
from websockets.models import Private_Conversation_Pair
from websockets.models import User_Private_Room_List

class Room_Chat_Error_Admin(admin.ModelAdmin):
    list_display = ('file', 'function_name', 'location_in_function',
                    'occurred_for_user','created', 'error_text')
    readonly_fields=('created', )
    filter_horizontal = ()
    list_filter = ['created', 'file', 'function_name',]

    class Meta:
        model = Room_Chat_Error

admin.site.register(Room_Chat_Error, Room_Chat_Error_Admin)

class Staff_Chat_Error_Admin(admin.ModelAdmin):
    list_display = ('file', 'function_name', 'location_in_function',
                    'occurred_for_user','created', 'error_text')
    readonly_fields=('created', )
    filter_horizontal = ()
    list_filter = ['created', 'file', 'function_name',]

    class Meta:
        model = Staff_Chat_Error

admin.site.register(Staff_Chat_Error, Staff_Chat_Error_Admin)

class User_Private_Room_List_Admin(admin.ModelAdmin):
    list_display = ['user','room_count','total_unread_private', 'date_created', 'last_updated']
    search_fields = ['user__username',]
    readonly_fields = ['date_created','last_updated' ]
    filter_horizontal = ['private_rooms',]
    list_filter = ['user',]

    class Meta:
        model = User_Private_Room_List

admin.site.register(User_Private_Room_List, User_Private_Room_List_Admin)


class Jitsi_Room_Unread_Chat_Message_Admin(admin.ModelAdmin):
    list_display = ['user','room','meeting_room', 'unread_count', 'date_created', "last_updated"]
    search_fields = ['user', ]
    readonly_fields = ['date_created', 'last_updated']
    list_filter = ['user', 'room','meeting_room']

    class Meta:
        model = Jitsi_Room_Unread_Chat_Message

admin.site.register(Jitsi_Room_Unread_Chat_Message, Jitsi_Room_Unread_Chat_Message_Admin)

class Staff_Room_Unread_Chat_Message_Admin(admin.ModelAdmin):
    list_display = ['user','room', 'unread_count', 'date_created', "last_updated"]
    search_fields = ['user', ]
    readonly_fields = ['date_created', 'last_updated']
    list_filter = ['user', 'room',]

    class Meta:
        model = Staff_Room_Unread_Chat_Message

admin.site.register(Staff_Room_Unread_Chat_Message, Staff_Room_Unread_Chat_Message_Admin)

class Help_Request_Admin(admin.ModelAdmin):
    list_display = [ 'from_user', 'from_room', 'room_url', 'created' , 'done']
    search_fields = [ ]
    readonly_fields = ['room_url', 'created' ]

    class Meta:
        model = Help_Request

admin.site.register(Help_Request, Help_Request_Admin)  

class Jitsi_Chat_Room_Admin(admin.ModelAdmin):
    list_display = ['id','title', 'slug', 'date_created']
    search_fields = ['id', 'title', ]
    readonly_fields = ['id', 'date_created']
    list_filter = ['title', 'date_created',]

    class Meta:
        model = Jitsi_Chat_Room


admin.site.register(Jitsi_Chat_Room, Jitsi_Chat_Room_Admin)

class Staff_Chat_Room_Admin(admin.ModelAdmin):
    list_display = ['id','title', 'slug', 'date_created']
    search_fields = ['id', 'title', ]
    readonly_fields = ['id', 'date_created']
    list_filter = ['title', 'date_created',]

    class Meta:
        model = Staff_Chat_Room


admin.site.register(Staff_Chat_Room, Staff_Chat_Room_Admin)

# Resource: http://masnun.rocks/2017/03/20/django-admin-expensive-count-all-queries/
class CachingPaginator(Paginator):
    def _get_count(self):

        if not hasattr(self, "_count"):
            self._count = None

        if self._count is None:
            try:
                key = "adm:{0}:count".format(hash(self.object_list.query.__str__()))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key, self._count, 3600)

            except:
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)


class Jitsi_Room_Chat_Message_Admin(admin.ModelAdmin):
    list_filter = ['room', 'display', 'meeting_room', 'user', "timestamp"]
    list_display = ['display','room','meeting_room', 'user', 'content',"timestamp"]
    search_fields = ['room__title', 'user__username','content']
    readonly_fields = ['id', "user", "room", "timestamp"]

    show_full_result_count = False
    paginator = CachingPaginator

    class Meta:
        model = Jitsi_Room_Chat_Message


admin.site.register(Jitsi_Room_Chat_Message, Jitsi_Room_Chat_Message_Admin)

class Staff_Room_Chat_Message_Admin(admin.ModelAdmin):
    list_filter = ['room', 'meeting_room', 'user', "timestamp"]
    list_display = ['room','meeting_room', 'user', 'content',"timestamp"]
    search_fields = ['room__title', 'user__username','content']
    readonly_fields = ['id',"timestamp"]

    show_full_result_count = False
    paginator = CachingPaginator

    class Meta:
        model = Staff_Room_Chat_Message

admin.site.register(Staff_Room_Chat_Message, Staff_Room_Chat_Message_Admin)


class Redirect_Admin(admin.ModelAdmin):
	list_display = ('user_to_redirect', 'to_room', 'redirect_url',
					'auto_send','created_by')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['created_by', 'user_to_redirect',]

	class Meta:
		model = Redirect

admin.site.register(Redirect, Redirect_Admin)


class Websocket_Error_Admin(admin.ModelAdmin):
	list_display = ('created','file', 'function_name', 'location_in_function',
					'occurred_for_user', 'error_text')
	readonly_fields=('created', )
	filter_horizontal = ()
	list_filter = ['created', 'file', 'function_name',]

	class Meta:
		model = Websocket_Error

admin.site.register(Websocket_Error, Websocket_Error_Admin)

class Socket_Group_Admin(admin.ModelAdmin):
	list_display = ('name', 'count', 'date_created', 'last_updated')
	readonly_fields=('date_created', 'last_updated' )
	filter_horizontal = ('connected_users',)

	class Meta:
		model = Socket_Group

admin.site.register(Socket_Group, Socket_Group_Admin)


class Notification_Admin(admin.ModelAdmin):
	list_display = ('target', 'from_user', 'verb','timestamp','read','content_type', 'object_id', 'content_object')
	readonly_fields=('timestamp', )
	filter_horizontal = ()
	list_filter = ['target', 'from_user', 'read']

	class Meta:
		model = Notification

admin.site.register(Notification, Notification_Admin)


class PrivateChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id','user1', 'user2', ]
    search_fields = ['id', 'user1__username', 'user2__username','user1__email', 'user2__email', ]
    readonly_fields = ['id',]

    class Meta:
        model = PrivateChatRoom


admin.site.register(PrivateChatRoom, PrivateChatRoomAdmin)

class RoomChatMessageAdmin(admin.ModelAdmin):
    list_filter = ['room','to_user', 'from_user', 'user', "timestamp"]
    list_display = ['room', 'to_user', 'from_user',  'user', 'content',"timestamp"]
    search_fields = ['user__username','content']
    readonly_fields = ['id', "user", "room", "timestamp"]

    show_full_result_count = False
    paginator = CachingPaginator

    class Meta:
        model = RoomChatMessage

admin.site.register(RoomChatMessage, RoomChatMessageAdmin)



class UnreadChatRoomMessagesAdmin(admin.ModelAdmin):
    list_display = ['room','user', 'count' ]
    search_fields = ['room__user1__username', 'room__user2__username', ]
    readonly_fields = ['id',]

    class Meta:
        model = UnreadChatRoomMessages

admin.site.register(UnreadChatRoomMessages, UnreadChatRoomMessagesAdmin)



# class Scheduled_Match_Status_NotificationList_Admin(admin.ModelAdmin):
# 	list_display = ('user', )
# 	readonly_fields=()
# 	filter_horizontal = ()
# 	list_filter = ['user',]

# 	class Meta:
# 		model = Scheduled_Match_Status_NotificationList

# admin.site.register(Scheduled_Match_Status_NotificationList, Scheduled_Match_Status_NotificationList_Admin)

# class User_Redirect_Notification_Admin(admin.ModelAdmin):
# 	list_display = ('user', )
# 	readonly_fields=()
# 	filter_horizontal = ()
# 	list_filter = ['user',]

# 	class Meta:
# 		model = User_Redirect_Notification

# admin.site.register(User_Redirect_Notification, User_Redirect_Notification_Admin)






# from websockets.models import Conversation

# user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="unread_staff")
#     room = models.ForeignKey(Staff_Chat_Room, on_delete=models.CASCADE, related_name="room_unread_staff")
#     unread_count = models.IntegerField(verbose_name="Unread Count", default=0)
#     date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
#     last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

# class Private_Conversation_Pair_Admin(admin.ModelAdmin):
#     list_display = ['user1','user1_has_unread', 'user2', 'user2_has_unread' ,'date_created', 'last_updated']
#     search_fields = []
#     readonly_fields = ['date_created','last_updated' ]
#     # filter_horizontal = ['messages',]

#     class Meta:
#         model = Private_Conversation_Pair

# admin.site.register(Private_Conversation_Pair, Private_Conversation_Pair_Admin)

# class Conversation_Admin(admin.ModelAdmin):
#     list_display = ['to_user','from_user','date_created', 'last_updated']
#     search_fields = []
#     readonly_fields = ['date_created','last_updated' ]
#     filter_horizontal = ['messages',]

#     class Meta:
#         model = Conversation

# admin.site.register(Conversation, Conversation_Admin)


# class Private_Message_Admin(admin.ModelAdmin):
#     list_display = ['from_user','to_user', 'message_read', 'read_at', "date_created"]
#     search_fields = []
#     readonly_fields = ['date_created', ]
#     list_filter = ['from_user', 'to_user', 'message_read', ]

#     class Meta:
#         model = Private_Message

# admin.site.register(Private_Message, Private_Message_Admin)