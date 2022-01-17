from django.contrib import admin
from users.models import CustomUser, Role
from jitsi_data.models import Jitsi_User_Status
from jitsi_data.models import Jitsi_Websocket_Error
from jitsi_data.models import Jitsi_Meeting_Room
from jitsi_data.models import Jitsi_ID

class Jitsi_ID_Admin(admin.ModelAdmin):
	list_display = ('jitsi_id','in_room', 'room', 'last_updated')
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['in_room','room',]
	search_fields = ()

	class Meta:
		model = Jitsi_ID

admin.site.register(Jitsi_ID, Jitsi_ID_Admin)

class Jitsi_User_Status_Admin(admin.ModelAdmin):
	list_display = ('user','online', 'room',)
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ('jitsi_ids',)
	list_filter = ['user__role','online','user', 'room']
	search_fields = ('user__full_name', 'user__username', )

	class Meta:
		model = Jitsi_User_Status

admin.site.register(Jitsi_User_Status, Jitsi_User_Status_Admin)

class Jitsi_Websocket_Error_Admin(admin.ModelAdmin):
	list_display = ('file', 'function_name', 'location_in_function',
					'occurred_for_user','created', 'error_text')
	readonly_fields=('created', )
	filter_horizontal = ()
	list_filter = ['created', 'file', 'function_name',]

	class Meta:
		model = Jitsi_Websocket_Error

admin.site.register(Jitsi_Websocket_Error, Jitsi_Websocket_Error_Admin)


class Jitsi_Meeting_Room_Admin(admin.ModelAdmin):
	list_display = ('room', 'occupied','student_alone','mismatch', 'count',)
	search_fields = ('name', )
	readonly_fields=()
	filter_horizontal = ('participants',  )
	list_filter = ['student_alone', 'room', 'occupied', ]

	class Meta:
		model = Jitsi_Meeting_Room

admin.site.register(Jitsi_Meeting_Room, Jitsi_Meeting_Room_Admin)