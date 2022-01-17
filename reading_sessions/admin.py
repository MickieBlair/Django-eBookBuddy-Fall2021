from django.contrib import admin
from users.models import CustomUser, Role
from reading_sessions.models import User_Session_Status, Connection_Drop
from reading_sessions.models import Match_Type, Temporary_Match_Type
from reading_sessions.models import Scheduled_Match, Temporary_Match
from reading_sessions.models import Match_Status_Option, Match_Status
from reading_sessions.models import Match_Attendance_Record
from reading_sessions.models import End_Session_Evaluation, Follow_Up_Type, Arrival_Description
from reading_sessions.models import Relational_Engagement, Evaluation_Level
from reading_sessions.models import API_Jitsi_Room_Participants
from reading_sessions.models import A_Problem_User, User_Status, Status_Redirect
from reading_sessions.models import Incomplete_Evaluation

# Register your models here.

class Incomplete_Evaluation_Admin(admin.ModelAdmin):
	list_display = ('user','reason','evaluation', )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['user', 'reason',]
	search_fields = ('user__full_name', 'user__username', 'reason' )

	class Meta:
		model = Incomplete_Evaluation

admin.site.register(Incomplete_Evaluation, Incomplete_Evaluation_Admin)

class User_Status_Admin(admin.ModelAdmin):
	list_display = ('user','online','in_room', 'has_ws_redirect', 'has_status_redirect',  'all_connected', 'max_reached', 'needs_to_reenter',)
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['online','has_ws_redirect', 'has_status_redirect', 'all_connected', 'max_reached', 'needs_to_reenter', 'last_updated','user', ]
	search_fields = ('user__full_name', 'user__username', )

	class Meta:
		model = User_Status

admin.site.register(User_Status, User_Status_Admin)

class Status_Redirect_Admin(admin.ModelAdmin):
	list_display = ('user_to_redirect', 'to_room', 'auto_send','created_by')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['created_by', 'user_to_redirect',]

	class Meta:
		model = Status_Redirect

admin.site.register(Status_Redirect, Status_Redirect_Admin)

class A_Problem_User_Admin(admin.ModelAdmin):
	list_display = ('date','user','room', 'comment', 'date_created',)
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['user__role','date_created','room','user']
	search_fields = ('user__full_name', 'user__username', )

	class Meta:
		model = A_Problem_User

admin.site.register(A_Problem_User, A_Problem_User_Admin)

class Connection_Drop_Admin(admin.ModelAdmin):
	list_display = ('date_created','user','room', )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['date_created', 'user','room']
	search_fields = ('user__full_name', 'user__username', )

	class Meta:
		model = Connection_Drop

admin.site.register(Connection_Drop, Connection_Drop_Admin)

class Evaluation_Level_Admin(admin.ModelAdmin):
	list_display = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Evaluation_Level

admin.site.register(Evaluation_Level, Evaluation_Level_Admin)

class Relational_Engagement_Admin(admin.ModelAdmin):
	list_display = ('name', 'desc')
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Relational_Engagement

admin.site.register(Relational_Engagement, Relational_Engagement_Admin)

class Follow_Up_Type_Admin(admin.ModelAdmin):
	list_display = ('name', )
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Follow_Up_Type

admin.site.register(Follow_Up_Type, Follow_Up_Type_Admin)

class Arrival_Description_Admin(admin.ModelAdmin):
	list_display = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Arrival_Description

admin.site.register(Arrival_Description, Arrival_Description_Admin)

class End_Session_Evaluation_Admin(admin.ModelAdmin):
	list_display = ('id','date','completed_by','student', 'follow_up_needed' )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['completed_by','scheduled_student', 'temp_student']
	search_fields = ('completed_by__full_name', 'completed_by__username', 'temp_student__full_name', 'temp_student__username', )

	class Meta:
		model = End_Session_Evaluation

	def student(self, obj):
		if obj.scheduled_student:
			return obj.scheduled_student.full_name
		elif obj.temp_student:
			return obj.temp_student.full_name
		else:
			return "None" 

admin.site.register(End_Session_Evaluation, End_Session_Evaluation_Admin)




class User_Session_Status_Admin(admin.ModelAdmin):
	list_display = ('id','user', 'full_name','logged_in','room','manual_redirect_on','role', 'needs_new_buddy', 'current_active_match_type','buddy', 'last_updated' )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['room','manual_redirect_on','needs_new_buddy', 'current_active_match_type', 'logged_in','user__role','temporary_buddy']
	search_fields = ('user__full_name', 'user__username')

	class Meta:
		model = User_Session_Status

	def full_name(self, obj):		
		return obj.user.full_name

	def role(self, obj):
		return obj.user.role

	def buddy(self, obj):
		if obj.scheduled_match:
			if obj.user.role.name == "Student":
				return obj.scheduled_match.volunteer.full_name
			elif obj.user.role.name == "Volunteer":
				return obj.scheduled_match.student.full_name
		else:
			return "None"

admin.site.register(User_Session_Status, User_Session_Status_Admin)

class Match_Type_Admin(admin.ModelAdmin):
	list_display = ('name', 'short_name' )
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Match_Type

admin.site.register(Match_Type, Match_Type_Admin)

class Temporary_Match_Type_Admin(admin.ModelAdmin):
	list_display = ('name', 'short_name' )
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Temporary_Match_Type

admin.site.register(Temporary_Match_Type, Temporary_Match_Type_Admin)

class Scheduled_Match_Admin(admin.ModelAdmin):
	list_display = ('id','student', 'volunteer', 'match_active', 'date_created', 'last_updated' )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ('scheduled_slots', 'sessions_scheduled', 'notes')
	list_filter = ['semester', ]
	search_fields = ('student__full_name', 'volunteer__full_name')
	class Meta:
		model = Scheduled_Match

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "student":
			kwargs["queryset"] = CustomUser.objects.filter(role__name='Student').order_by('username')
		if db_field.name == "volunteer":
			kwargs["queryset"] = CustomUser.objects.filter(role__name='Volunteer').order_by('username')
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Scheduled_Match, Scheduled_Match_Admin)

class Temporary_Match_Admin(admin.ModelAdmin):
	list_display = ('id','session', 'temp_type', 'student_user', 'teacher_user', 'match_active', 'date_created', 'last_updated' )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ('notes',)
	list_filter = ["student_user__full_name", 'teacher_user__full_name', 'temp_type',  'match_active','session__semester', 'session', ]
	search_fields = ('student_user__full_name', 'student_user__username', 'teacher_user__full_name', 'teacher_user__username',)
	class Meta:
		model = Temporary_Match

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "student_user":
			kwargs["queryset"] = CustomUser.objects.filter(role__name='Student').order_by('username')
		if db_field.name == "teacher_user":
			kwargs["queryset"] = CustomUser.objects.all().exclude(role__name='Student').order_by('username')
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Temporary_Match, Temporary_Match_Admin)

class Match_Status_Option_Admin(admin.ModelAdmin):
	list_display = ('name', )
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Match_Status_Option

admin.site.register(Match_Status_Option, Match_Status_Option_Admin)

class Match_Status_Admin(admin.ModelAdmin):
	list_display = ('id','session', 'match_status_active', 'member_reassigned',
						'vol_reassigned', 'student_reassigned', 'type', 'match', 'last_updated' )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['session__date','session__day_time', 'session','match_type', 'match_status_active', 'sch_match', 'temp_match', ]
	search_fields = ('sch_match__student__full_name', 'sch_match__volunteer__full_name')
	
	class Meta:
		model = Match_Status

	def type(self, obj):
		if obj.match_type.name == "Scheduled":
			return obj.match_type.name			
		else:
			if obj.match_type.name == "Temporary":
				return obj.match_type.name + " - " + obj.temp_match.temp_type.name

	def match(self, obj):
		if obj.match_type.name == "Scheduled":
			return obj.sch_match			
		else:
			if obj.match_type.name == "Temporary":
				return obj.temp_match

admin.site.register(Match_Status, Match_Status_Admin)

class Match_Attendance_Record_Admin(admin.ModelAdmin):
	list_display = ('id','session', 'type', 'match', 'last_updated' )
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['session__date','session__day_time', 'session','match_type',
				'sch_match', 'temp_match__temp_type', 'temp_match', ]
	search_fields = ('sch_match__student__full_name', 'sch_match__volunteer__full_name')
	
	class Meta:
		model = Match_Attendance_Record

	def type(self, obj):
		if obj.match_type.name == "Scheduled":
			return obj.match_type.name			
		else:
			if obj.match_type.name == "Temporary":
				return obj.match_type.name + " - " + obj.temp_match.temp_type.name

	def match(self, obj):
		if obj.match_type.name == "Scheduled":
			return obj.sch_match			
		else:
			if obj.match_type.name == "Temporary":
				return obj.temp_match

admin.site.register(Match_Attendance_Record, Match_Attendance_Record_Admin)