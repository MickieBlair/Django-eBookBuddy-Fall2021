from django.contrib import admin
from site_admin.models import Server_Time, Site_View_Error
from site_admin.models import Daily_Session
from site_admin.models import Day
from site_admin.models import Day_With_Daily_Session
from site_admin.models import Note
from site_admin.models import Note_Group, Note_Category
from site_admin.models import Reading_Level
from site_admin.models import Room
from site_admin.models import Room_Type
from site_admin.models import Semester
from site_admin.models import Session_Day_Time
from site_admin.models import Session_Reading_Level
from site_admin.models import Student_Progress, Student_Assessment
from site_admin.models import User_Log
from site_admin.models import Gender, Language, Grade, School
from site_admin.models import Student_Profile, Volunteer_Profile, Staff_Profile
from site_admin.models import System_Message
from site_admin.models import Mega_Team, Team
from site_admin.models import Upload_CSV
from site_admin.models import Volunteer_Report, Student_Report, Sign_In_By_Day
from site_admin.models import Attendance_Status
from site_admin.models import Team_Meeting,Day_With_Team_Meeting, Day_With_Orientation_Meeting
from site_admin.models import Sign_In_By_User

class Sign_In_By_User_Admin(admin.ModelAdmin):
	list_display = ('user','diff_count', 'total_sign_ins', 'missing_out','total_minutes', 'total_hours', 'problem_user')
	readonly_fields=()
	filter_horizontal = ('logs',)
	list_filter = ['user__role', 'user',]
	search_fields = ('user__role', 'user__username', 'user__full_name')

	class Meta:
		model = Sign_In_By_User

admin.site.register(Sign_In_By_User, Sign_In_By_User_Admin)


class Day_With_Orientation_Meeting_Admin(admin.ModelAdmin):
	list_display = ('date', 'time_start', 'time_end')
	readonly_fields=()
	filter_horizontal = ('allowed_participants',)
	list_filter = [ 'date', ]
	search_fields = ()

	class Meta:
		model = Day_With_Orientation_Meeting

admin.site.register(Day_With_Orientation_Meeting, Day_With_Orientation_Meeting_Admin)

class Day_With_Team_Meeting_Admin(admin.ModelAdmin):
	list_display = ('date', 'day', )
	readonly_fields=()
	filter_horizontal = ()
	list_filter = [ 'day', ]
	search_fields = ()

	class Meta:
		model = Day_With_Team_Meeting

admin.site.register(Day_With_Team_Meeting, Day_With_Team_Meeting_Admin)

class Team_Meeting_Admin(admin.ModelAdmin):
	list_display = ('team', 'day', 'time')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['team', 'day', ]
	search_fields = ('team__name',)

	class Meta:
		model = Team_Meeting

admin.site.register(Team_Meeting, Team_Meeting_Admin)

class Attendance_Status_Admin(admin.ModelAdmin):
	list_display = ('name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = []

	class Meta:
		model = Attendance_Status

admin.site.register(Attendance_Status, Attendance_Status_Admin)

class Volunteer_Report_Admin(admin.ModelAdmin):
	list_display = ('user', 'no_logs', 'total_sign_ins')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['user__role', 'user', 'no_logs',]
	search_fields = ('user__username', 'user__full_name')

	class Meta:
		model = Volunteer_Report

admin.site.register(Volunteer_Report, Volunteer_Report_Admin)

class Student_Report_Admin(admin.ModelAdmin):
	list_display = ('user', 'no_logs', 'total_sign_ins')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['user__role', 'user', 'no_logs',]
	search_fields = ('user__username', 'user__full_name')

	class Meta:
		model = Student_Report

admin.site.register(Student_Report, Student_Report_Admin)

class Sign_In_By_Day_Admin(admin.ModelAdmin):
	list_display = ('day', 'session', 'user','total_sign_ins', 'total_minutes')
	readonly_fields=()
	filter_horizontal = ('logs',)
	list_filter = ['user__role', 'day', 'user',]
	search_fields = ('user__role', 'user__username', 'user__full_name')

	class Meta:
		model = Sign_In_By_Day

admin.site.register(Sign_In_By_Day, Sign_In_By_Day_Admin)

class Upload_CSV_Admin(admin.ModelAdmin):
	list_display = ('name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = []

	class Meta:
		model = Upload_CSV

admin.site.register(Upload_CSV, Upload_CSV_Admin)

class Mega_Team_Admin(admin.ModelAdmin):
	list_display = ('name', 'coordinator','date_created', 'last_updated',)
	search_fields = ('name', 'coordinator__full_name',)
	readonly_fields=('date_created', 'last_updated',)
	filter_horizontal = ('team_leaders', 'volunteers')
	list_filter = ('coordinator__full_name', )
	fieldsets = ()

	class Meta:
		model = Mega_Team

admin.site.register(Mega_Team, Mega_Team_Admin)

class Team_Admin(admin.ModelAdmin):
	list_display = ('name', 'mega', 'leader','room', 'date_created', 'last_updated',)
	search_fields = ('name', 'leader__full_name', 'mega__name')
	readonly_fields=('date_created', 'last_updated',)
	filter_horizontal = ('volunteers',)
	list_filter = ('mega', 'leader__full_name', )
	fieldsets = ()

	class Meta:
		model = Team

admin.site.register(Team, Team_Admin)


class System_Message_Admin(admin.ModelAdmin):
	list_display = ('name', 'eng_message', 'span_message')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = []

	class Meta:
		model = System_Message

admin.site.register(System_Message, System_Message_Admin)

class Site_View_Error_Admin(admin.ModelAdmin):
	list_display = ('module', 'view', 'location_in_view',
					'occurred_for_user','created', 'error_text')
	readonly_fields=('created', )
	filter_horizontal = ()
	list_filter = ['module', 'view',]

	class Meta:
		model = Site_View_Error

admin.site.register(Site_View_Error, Site_View_Error_Admin)

class Server_Time_Admin(admin.ModelAdmin):
	list_display = ('name','mon_vol_start','mon_vol_end', 'vol_start','vol_end', 'start_time', 'end_time',
					'active','entry_allowed_start', 'entry_allowed_end',)
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ('days',)
	list_filter = ['name', 'active']

	class Meta:
		model = Server_Time

admin.site.register(Server_Time, Server_Time_Admin)

class Session_Reading_Level_Admin(admin.ModelAdmin):
	list_display = ('session', 'user', 'full_name','level','date','updated_by', 'last_updated',)
	search_fields = ('user', 'user__full_name',)
	readonly_fields=()
	filter_horizontal = ('level_notes',)
	list_filter = ('user__full_name', 'user', 'session')
	fieldsets = ()

	class Meta:
		model = Session_Reading_Level

	def full_name(self, obj):		
		return obj.user.full_name

admin.site.register(Session_Reading_Level, Session_Reading_Level_Admin)

class Student_Assessment_Admin(admin.ModelAdmin):
	list_display = ('date', 'user', 'full_name','level','assessed_by',)
	search_fields = ('user', 'user__full_name',)
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ('user__full_name', 'user', 'assessed_by',)
	fieldsets = ()

	class Meta:
		model = Student_Assessment

	def full_name(self, obj):		
		return obj.user.full_name

admin.site.register(Student_Assessment, Student_Assessment_Admin)

class Student_Progress_Admin(admin.ModelAdmin):
	list_display = ('user', 'full_name','initial_assessment', 'starting','current','end','last_assessed',)
	search_fields = ('user', 'user__full_name',)
	readonly_fields=()
	filter_horizontal = ('level_progress', 'progress_notes', 'assessments',)
	list_filter = ('initial_assessment', 'user__user_dropped', 'user__full_name', 'user', )
	fieldsets = ()

	class Meta:
		model = Student_Progress

	def full_name(self, obj):		
		return obj.user.full_name

admin.site.register(Student_Progress, Student_Progress_Admin)


class Gender_Admin(admin.ModelAdmin):
	list_display = ('name', 'span')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Gender

admin.site.register(Gender, Gender_Admin)

class Language_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Language

admin.site.register(Language, Language_Admin)

class School_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = School

admin.site.register(School, School_Admin)

class Grade_Admin(admin.ModelAdmin):
	list_display = ('name','short_name', 'letter')
	search_fields = ('name','short_name')
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Grade

admin.site.register(Grade, Grade_Admin)

class Student_Profile_Admin(admin.ModelAdmin):
	list_display = ('user', 'full_name','gender', 'age','primary_lang',
					'secondary_lang','last_updated',)
	search_fields = ('user', 'user__full_name',)
	readonly_fields=()

	filter_horizontal = ('available_day_time_slots', 'scheduled_day_time_slots', 'profile_notes')
	list_filter = ()
	fieldsets = ()

	class Meta:
		model = Student_Profile

	def full_name(self, obj):		
		return obj.user.full_name

admin.site.register(Student_Profile, Student_Profile_Admin)

class Volunteer_Profile_Admin(admin.ModelAdmin):
	list_display = ('user', 'full_name','mega','team','gender','primary_lang',
					'secondary_lang','last_updated',)
	search_fields = ('user', 'user__full_name',)
	readonly_fields=()

	filter_horizontal = ('available_day_time_slots', 'scheduled_day_time_slots', 'profile_notes')
	list_filter = ('mega','team')
	fieldsets = ()

	class Meta:
		model = Volunteer_Profile

	def full_name(self, obj):		
		return obj.user.full_name
		
admin.site.register(Volunteer_Profile, Volunteer_Profile_Admin)

class Staff_Profile_Admin(admin.ModelAdmin):
	list_display = ('user', 'full_name','gender','primary_lang',
					'secondary_lang','last_updated',)
	search_fields = ('user', 'user__full_name',)
	readonly_fields=()

	filter_horizontal = ('profile_notes',)
	list_filter = ()
	fieldsets = ()

	class Meta:
		model = Staff_Profile

	def full_name(self, obj):		
		return obj.user.full_name
		
admin.site.register(Staff_Profile, Staff_Profile_Admin)

class Daily_Session_Admin(admin.ModelAdmin):
	list_display = ('id','name', 'semester','session_complete','day_time','date','slug', 'date_created', 'last_updated', 'archive_session')
	search_fields = ()
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['semester', 'archive_session', 'day_time', ]
	search_fields = ('name',)

	class Meta:
		model = Daily_Session

admin.site.register(Daily_Session, Daily_Session_Admin)

class Day_Admin(admin.ModelAdmin):
	list_display = ('number', 'name','letter',  'span_name', 'short_name' )
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Day

admin.site.register(Day, Day_Admin)

class Day_With_Daily_Session_Admin(admin.ModelAdmin):
	search_fields = ('day__name',)
	list_display = ('id','date','day' ,'semester', 'count', 'all_complete')
	readonly_fields=()
	filter_horizontal = ('day_sessions', )
	list_filter = ['date', 'day', 'semester', ]

	class Meta:
		model = Day_With_Daily_Session

admin.site.register(Day_With_Daily_Session, Day_With_Daily_Session_Admin)

class Note_Group_Admin(admin.ModelAdmin):
	list_display = ('name', )
	readonly_fields=()
	filter_horizontal = ()
	list_filter = []

	class Meta:
		model = Note_Group

admin.site.register(Note_Group, Note_Group_Admin)


class Note_Category_Admin(admin.ModelAdmin):
	list_display = ('group','name', )
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['group',]

	class Meta:
		model = Note_Category

admin.site.register(Note_Category, Note_Category_Admin)

class Note_Admin(admin.ModelAdmin):
	list_display = ('category', 'author', 'date_created', 'last_updated')
	readonly_fields=('date_created', 'last_updated')
	filter_horizontal = ()
	list_filter = ['category', 'author__role',]

	class Meta:
		model = Note

admin.site.register(Note, Note_Admin)

class Reading_Level_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Reading_Level

admin.site.register(Reading_Level, Reading_Level_Admin)


class Room_Admin(admin.ModelAdmin):
	list_display = ('name', 'occupied', 'num_participants',
					'jitsi_num_participants','number','room_type_letter', 'slug')
	search_fields = ('name', )
	readonly_fields=()
	filter_horizontal = ('participants', 'jitsi_participants' )
	list_filter = ['room_type', 'occupied', ]

	class Meta:
		model = Room

	def room_type_letter(self, obj):
		return obj.room_type.letter

admin.site.register(Room, Room_Admin)

class Room_Type_Admin(admin.ModelAdmin):
	list_display = ('name', 'letter', )
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Room_Type

admin.site.register(Room_Type, Room_Type_Admin)

class Semester_Admin(admin.ModelAdmin):
	list_display = ('name','active_semester', 'start_date', 'end_date', 'date_created', 'last_updated')
	search_fields = ('name',)
	readonly_fields=('date_created', 'last_updated', 'days')
	filter_horizontal = ('day_time_slots',)

	class Meta:
		model = Semester

admin.site.register(Semester, Semester_Admin)

class Session_Day_Time_Admin(admin.ModelAdmin):
	list_display = ('day','time_start', 'time_end', 'session_slot')
	search_fields = ()
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Session_Day_Time

admin.site.register(Session_Day_Time, Session_Day_Time_Admin)

class User_Log_Admin(admin.ModelAdmin):
	search_fields = ('user__full_name',)
	list_display = ('id', 'user','role' ,'room', 'time_in','time_out', 'logged_in', 'duration_seconds')
	readonly_fields=()
	filter_horizontal = ()
	list_filter = ['date_created', 'user__role', 'logged_in', 'user', 'room', 'logged_in']

	class Meta:
		model = User_Log

	def role(self, obj):
		return obj.user.role

admin.site.register(User_Log, User_Log_Admin)


