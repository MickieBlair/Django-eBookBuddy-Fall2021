from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
import datetime
from users.models import Role, CustomUser
import math

# Create your models here.



class Upload_CSV(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	csv_file = models.FileField(upload_to='uploads/initial/')
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['name']
		verbose_name = 'Upload CSV'
		verbose_name_plural = 'Upload CSVs'

	def __str__(self):
		return self.name

@receiver(post_delete, sender=Upload_CSV)
def upload_csv_delete(sender, instance, **kwargs):
	instance.csv_file.delete(False)

class Mega_Team(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	coordinator = models.ForeignKey(CustomUser, related_name="mega_coordinator",
					blank=True, null=True, on_delete=models.CASCADE)
	team_leaders = models.ManyToManyField(CustomUser, related_name="mega_team_leaders",
					blank=True,)
	volunteers = models.ManyToManyField(CustomUser, related_name="mega_team_vol",
					blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Mega Team'
		verbose_name_plural = 'Mega Teams'

	def __str__(self):
		return self.name



class System_Message(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	eng_message = models.TextField(max_length=2000, null=True, blank=True) 
	span_message = models.TextField(max_length=2000, null=True, blank=True) 
	class Meta:
		ordering = ['name']
		verbose_name = 'System Message'
		verbose_name_plural = 'System Messages'

	def __str__(self):
		return self.name

class Site_View_Error(models.Model):
	module = models.CharField(max_length=255, null=True, blank=True)
	view = models.CharField(max_length=255, null=True, blank=True)
	location_in_view = models.CharField(max_length=255, null=True, blank=True)		
	occurred_for_user = models.CharField(max_length=255, null=True, blank=True)
	error_text = models.TextField(max_length=2000, null=True, blank=True)
	created	= models.DateTimeField(verbose_name='created', auto_now_add=True)

	class Meta:
		ordering = ['-created']
		verbose_name = 'Site View Error'
		verbose_name_plural = 'Site View Errors'

	def __str__(self):
		return self.module + ": " + self.module

class Day(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	span_name = models.CharField(max_length=100, null=False, blank=True) 
	number = models.IntegerField(null=True, blank=True)
	short_name = models.CharField(max_length=3, null=True, blank=True)
	letter = models.CharField(max_length=3, null=True, blank=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Day'
		verbose_name_plural = 'Days'

	def __str__(self):
		return self.name

class Server_Time(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	start_time = models.TimeField(blank=True, null=True)
	end_time = models.TimeField(blank=True, null=True)
	offset = models.IntegerField(null=True, blank=True, help_text="-240 DST, -300 no DST")
	active = models.BooleanField(default=True)
	days = models.ManyToManyField(Day, related_name="server_days", blank=True,)
	entry_allowed_start = models.TimeField(blank=True, null=True)
	entry_allowed_end = models.TimeField(blank=True, null=True)
	student_start = models.TimeField(blank=True, null=True)
	student_end = models.TimeField(blank=True, null=True)
	mon_vol_start = models.TimeField(blank=True, null=True)
	mon_vol_end = models.TimeField(blank=True, null=True)
	vol_start = models.TimeField(blank=True, null=True)
	vol_end = models.TimeField(blank=True, null=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['name']
		verbose_name = 'Server Time'
		verbose_name_plural = 'Server Times'

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if self.active:
			qs = type(self).objects.filter(active=True)
			if self.pk:
				qs = qs.exclude(pk=self.pk)
			qs.update(active=False) 		

		super(Server_Time, self).save(*args, **kwargs)

		date_now = timezone.now()

		start_time = datetime.datetime(date_now.year, date_now.month,
												date_now.day, self.start_time.hour,
												self.start_time.minute, self.start_time.second)

		end_time = datetime.datetime(date_now.year, date_now.month,
												date_now.day, self.end_time.hour,
												self.end_time.minute, self.end_time.second)

		ten_minutes = datetime.timedelta(minutes=10)
		fifteen_minutes = datetime.timedelta(minutes=15)

		entry_start = start_time - ten_minutes
		entry_end = end_time - fifteen_minutes

		self.entry_allowed_start = str(entry_start.hour) + ":" + str(entry_start.minute) +":"+ str(entry_start.second)
		self.entry_allowed_end = str(entry_end.hour) + ":" + str(entry_end.minute) +":"+ str(entry_end.second)

		super(Server_Time, self).save(*args, **kwargs)




class Gender(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	span = models.CharField(max_length=100, null=True, blank=True)
	letter = models.CharField(max_length=1, null=True, blank=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Gender'
		verbose_name_plural = 'Genders'

	def __str__(self):
		return self.name

class School(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		ordering = ['name']
		verbose_name = 'School'
		verbose_name_plural = 'Schools'

	def __str__(self):
		return self.name

class Grade(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	short_name = models.CharField(max_length=100, null=True, blank=True)
	letter = models.CharField(max_length=1, null=True, blank=True)
	
	class Meta:
		ordering = ['name']
		verbose_name = 'Grade'
		verbose_name_plural = 'Grades'

	def __str__(self):
		return self.name

class Language(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		ordering = ['name']
		verbose_name = 'Language'
		verbose_name_plural = 'Languages'

	def __str__(self):
		return self.name

class Note_Group(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Note Group'
		verbose_name_plural = 'Note Groups'

	def __str__(self):
		return self.name

class Note_Category(models.Model):
	group = models.ForeignKey(Note_Group, related_name="note_group",
										on_delete=models.CASCADE, null=True, blank=True,)
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Note Category'
		verbose_name_plural = 'Note Categories'

	def __str__(self):
		return self.name

class Note(models.Model):
	category = models.ForeignKey(Note_Category, related_name="notes_category",
										on_delete=models.CASCADE)
	author = models.ForeignKey(CustomUser, related_name="made_by",
										on_delete=models.CASCADE)
	content = models.TextField(max_length=2000, null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		verbose_name = 'Note'
		verbose_name_plural = 'Notes'

	def __str__(self):
		str_for_return = self.category.name + " - " + self.author.username + " Note"
		return str_for_return

class Room_Type(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	letter = models.CharField(max_length=1, null=False, blank=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Room Type'
		verbose_name_plural = 'Room Types'

	def __str__(self):
		return self.name

class Room(models.Model):
	name = models.CharField(max_length=150, blank=False, unique=True)
	number = models.IntegerField(blank=True, null=True)
	room_type = models.ForeignKey(Room_Type, on_delete=models.CASCADE, related_name="type_room",
								 null=True, blank=True, verbose_name="Room Type")
	slug = models.SlugField(blank=True, unique=True, max_length=255,)
	room_url = models.URLField(max_length=500, null=True, blank=True)
	occupied = models.BooleanField(default=False)
	num_participants = models.IntegerField(verbose_name="Count", default=0)
	participants = models.ManyToManyField(CustomUser, related_name="room_participants", blank=True,)
	jitsi_num_participants = models.IntegerField(verbose_name="Jitsi Count", default=0)
	jitsi_participants = models.ManyToManyField(CustomUser, related_name="jitsi_participants", blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def in_room(self):
		return self.participants.all()

	def add_participant(self, user):
		self.participants.add(user)
		if self.participants.all().count() == 0:
			self.num_participants = 0
			self.occupied = False
		else:
			self.num_participants = self.participants.all().count()
			self.occupied = True
		self.save()
		# print("ADDED", self.num_participants)
		return self.participants.all()

	def remove_participant(self,user):
		self.participants.remove(user)
		if self.participants.all().count() == 0:
			self.num_participants = 0
			self.occupied = False
		else:
			self.num_participants = self.participants.all().count()
			self.occupied = True
		self.save()
		# print("REMOVED", self.num_participants)
		return self.participants.all()

	def unoccupied_breakout_first():
		room = Room.objects.filter(name__contains="Breakout", occupied=False).first()
		return room

	def get_count(self):
		if self.participants.all().count() == 0:
			self.num_participants = 0
			self.occupied = False
		else:
			self.num_participants = self.participants.all().count()
			self.occupied = True
		self.save()


	class Meta:
		ordering = ['id']
		verbose_name = 'Room'
		verbose_name_plural = 'Rooms'

	def __str__(self):
		return self.name

def pre_save_room_receiver(sender, instance, *args, **kwargs):
	# print("ROOM Receiver, presave")
	# count = instance.participants.all().count()
	# print("Count in room", count)
	# if count == 0:
	# 	instance.occupied == False
	# 	instance.num_participants = 0

	# else:
	# 	instance.occupied = True
	# 	instance.num_participants = instance.participants.all().count()

	
	# if instance.slug == None:
	instance.slug = slugify(instance.name)
	instance.room_url = settings.BASE_URL + "/sessions/room/" + instance.slug +"/"

	

pre_save.connect(pre_save_room_receiver, sender=Room)

# def post_save_room_receiver(sender, instance, *args, **kwargs):
# 	jitsi, created = Jitsi_Meeting.objects.get_or_create(room=instance)

# post_save.connect(post_save_room_receiver, sender=Room)

class Team(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	mega = models.ForeignKey(Mega_Team, related_name="mega_team",
					blank=True, null= True, on_delete=models.SET_NULL)
	leader = models.ForeignKey(CustomUser, related_name="team_leader",
					blank=True, null=True, on_delete=models.SET_NULL)
	volunteers = models.ManyToManyField(CustomUser, related_name="team_vols",
					blank=True,)
	room = models.ForeignKey(Room, related_name="team_room",
					blank=True, null= True, on_delete=models.SET_NULL)
	meeting_day = models.ForeignKey(Day, related_name="team_meeting_day", on_delete=models.CASCADE ,null=True, blank=True)
	meeting_time = models.TimeField(null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def get_mega_and_team(self):
		str_for_return = self.mega.name + " - " + self.name
		return str_for_return

	class Meta:
		ordering = ['id']
		verbose_name = 'Team'
		verbose_name_plural = 'Teams'

	def __str__(self):
		return self.name	

#Sessions
class Session_Day_Time(models.Model):	
	day = models.ForeignKey(Day, on_delete=models.CASCADE ,null=False, blank=False)
	time_start = models.TimeField(null=False, blank=False)
	time_end = models.TimeField(null=False, blank=False)
	session_slot = models.CharField(max_length=1, null=False, blank=False)
	currently_active = models.BooleanField(default=True)

	class Meta:
		ordering = ['day__number', 'session_slot']
		verbose_name = 'Session Day/Time'
		verbose_name_plural = 'Session Days/Times'

	def get_short_name(self):
		return self.day.short_name + "-" + self.session_slot

	def get_name_time(self):
		str_time = self.time_start.strftime("%I:%M %p")
		return self.day.short_name + "-" + self.session_slot + "-" + str_time

	def get_slot_session_times(self):
		str_time_start = self.time_start.strftime("%I:%M %p")
		str_time_end = self.time_end.strftime("%I:%M %p")
		return self.session_slot + ": " + str_time_start + " - " + str_time_end

	def __str__(self):
		return self.day.name + " - " + self.session_slot

class Semester(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	start_date = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)
	end_date = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)
	active_semester = models.BooleanField(default=False)
	days = models.ManyToManyField(Day, related_name="days_in_session", blank=True,)
	day_time_slots = models.ManyToManyField(Session_Day_Time, related_name="semester_slots", blank=True,)
	full_dates = models.CharField(max_length=100, null=True, blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	slug = models.SlugField(blank=True, unique=True, max_length=255,)

	def active_sessions_in_semester(self):
		sessions = Daily_Session.objects.filter(semester = self, archive_session=False)
		return sessions

	# def sessions_in_semester(self):
	# 	sessions = Daily_Session.objects.filter(semester = self)
	# 	return sessions	

	class Meta:
		ordering = ['id']
		verbose_name = 'Semester'
		verbose_name_plural = 'Semesters'

	def __str__(self):
		return self.name

@receiver(pre_save, sender=Semester)
def auto_populate_full_description(sender, instance=None, created=False, **kwargs):
	start_date = instance.start_date.strftime("%B %d, %Y")
	end_date = instance.end_date.strftime("%B %d, %Y")
	instance.full_dates = start_date + ' - ' + end_date
	instance.slug = slugify(instance.name)


class Daily_Session(models.Model):
	semester =  models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='daily_sessions', null=True, blank=True)
	day_time = models.ForeignKey(Session_Day_Time, related_name="session_day_time",
								 on_delete=models.CASCADE ,null=True, blank=True)
	slug = models.SlugField(blank=True, max_length=255,)
	date = models.DateField(verbose_name="Date", null=True, blank=True)
	week = models.IntegerField(default = 0)
	session_complete = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	name = models.CharField(max_length=255, null=True, blank=True)
	archive_session = models.BooleanField(default=False, verbose_name="Archived")
	session_start_date_time = models.DateTimeField(verbose_name="Start Date/Time", blank=True, null=True)
	session_end_date_time = models.DateTimeField(verbose_name="Start Date/Time", blank=True, null=True)
	entry_allowed_start = models.DateTimeField(blank=True, null=True)
	entry_allowed_end = models.DateTimeField(blank=True, null=True)
	student_entry_allowed_start = models.DateTimeField(blank=True, null=True)
	student_entry_allowed_end = models.DateTimeField(blank=True, null=True)	

	def todays_sessions(date):
		sessions = Daily_Session.objects.filter(date=date).order_by('session_start_date_time')
		return sessions

	def short_name(self):
		str_for_return = str(self.day_time.get_slot_session_times())
		return str_for_return

	def date_session_slot(self):
		str_for_return = self.date.strftime("%B %d, %Y") + ' - ' +self.day_time.session_slot
		return str_for_return 

	def short_date_day_session_slot(self):
		str_for_return = self.date.strftime("%b %d") +' - '+ self.day_time.day.short_name +' - ' +self.day_time.session_slot
		return str_for_return 

	def month_day_session_slot(self):
		str_for_return = self.date.strftime("%b %d") + ' - ' +self.day_time.session_slot
		return str_for_return  

	def active_scheduled_matches_in_session(self):
		matches = self.scheduled_matches_in_session.filter(match_active=True)
		return matches

	def all_attendance_records(self):
		# session = Daily_Session.objects.get(pk=self.id)
		records = self.match_attendance_session.all()
		# print("\nRecords", self, records)
		return records

	def scheduled_attendance_records(self):
		# session = Daily_Session.objects.get(pk=self.id)
		records = self.match_attendance_session.filter(match_type__name="Scheduled")
		# print("\nRecords", self, records)
		return records

	def temporary_attendance_records(self):
		# session = Daily_Session.objects.get(pk=self.id)
		records = self.match_attendance_session.filter(match_type__name="Temporary")
		# print("\nRecords", self, records)
		return records

	def all_match_statuses(self):
		# session = Daily_Session.objects.get(pk=self.id)
		records = self.match_status_session.all()
		# print("\nRecords", self, records)
		return records

	def successful_sch_matches(self):
		successful = self.match_attendance_session.filter(match_type__name="Scheduled",
			match_successful=True)
		return successful

	def number_successful_matches(self):
		successful = self.match_attendance_session.filter(match_successful=True).count()
		return successful

	def percent_successful_sch_matches(self):
		all_scheduled_complete = self.match_attendance_session.filter(match_type__name="Scheduled",
								match_successful=True).count()
		all_scheduled = self.match_attendance_session.filter(match_type__name="Scheduled").count()
		print("All scheduled Count", all_scheduled)

		
		# print("count_of_all", count_of_all)
		if all_scheduled != 0:
			# print("not zero")
			# print("query",self.session_attendance_record.filter(match_successful=True))
			successful = all_scheduled_complete
			percent_i = (successful/all_scheduled) * 100
			percent = round(percent_i, 2)
			str_for_return = str(percent) + " %"
		else:
			# print("zero")
			str_for_return = "No Matches"
		# print("str_for_return", str_for_return)
		return str_for_return

	class Meta:
		ordering = ['date', 'day_time']
		verbose_name = 'Session'
		verbose_name_plural = 'Sessions'

	def __str__(self):
		return self.name

	
def pre_save_daily_session_receiver(sender, instance, *args, **kwargs):
	instance.name =  instance.date.strftime("%B %d, %Y") + " - " + instance.day_time.day.name + " " + instance.day_time.session_slot
	instance.slug = slugify(instance.name)


	start_date_time = datetime.datetime(instance.date.year,
														 instance.date.month,
														 instance.date.day,
														 instance.day_time.time_start.hour,
														 instance.day_time.time_start.minute,
														 instance.day_time.time_start.second)

	end_date_time = datetime.datetime(instance.date.year,
														 instance.date.month,
														 instance.date.day,
														 instance.day_time.time_end.hour,
														 instance.day_time.time_end.minute,
														 instance.day_time.time_end.second)

	instance.session_start_date_time = start_date_time
	instance.session_end_date_time = end_date_time

	five_minutes = datetime.timedelta(minutes=5)
	ten_minutes = datetime.timedelta(minutes=10)
	fifteen_minutes = datetime.timedelta(minutes=15)

	entry_start = start_date_time - ten_minutes
	entry_end = end_date_time + ten_minutes

	stu_entry_start = start_date_time - five_minutes
	stu_entry_end = end_date_time + ten_minutes

	# self.entry_allowed_start = str(entry_start.hour) + ":" + str(entry_start.minute) +":"+ str(entry_start.second)
	# self.entry_allowed_end = str(entry_end.hour) + ":" + str(entry_end.minute) +":"+ str(entry_end.second)

	instance.entry_allowed_start = str(entry_start)
	instance.entry_allowed_end = str(entry_end)
	instance.student_entry_allowed_start = str(stu_entry_start)
	instance.student_entry_allowed_end = str(stu_entry_end)



pre_save.connect(pre_save_daily_session_receiver, sender=Daily_Session)

def post_save_daily_session_receiver(sender, instance, *args, **kwargs):
	if not instance.archive_session:
		day_with_session, created = Day_With_Daily_Session.objects.get_or_create(date = instance.date,
																		day = instance.day_time.day, 
																		semester = instance.semester)
		day_with_session.add_session(instance)
	else:
		day_with_session, created = Day_With_Daily_Session.objects.get_or_create(date = instance.date,
																		day = instance.day_time.day, 
																		semester = instance.semester)
		day_with_session.remove_session(instance)


post_save.connect(post_save_daily_session_receiver, sender=Daily_Session)



class Day_With_Daily_Session(models.Model):
	date = models.DateField(verbose_name="Date", unique=True)
	day = models.ForeignKey(Day, on_delete=models.CASCADE ,null=False, blank=False) 
	semester =  models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='semester_day', null=True, blank=True)
	day_sessions = models.ManyToManyField(Daily_Session,
									 related_name="day_sessions",
									 blank=True,)
	week = models.IntegerField(default = 0)
	count = models.IntegerField(default = 0)
	all_complete = models.BooleanField(default=False)
	total_matches = models.IntegerField(default=0)
	total_active_scheduled = models.IntegerField(default=0)
	total_temporary = models.IntegerField(default=0)
	total_complete_scheduled_matches = models.IntegerField(default=0)
	percent_successful = models.DecimalField(default=0, max_digits=5, decimal_places=2)
	total_complete_reading_count = models.IntegerField(default=0)

	def add_session(self, session):
		self.day_sessions.add(session)
		self.count = self.day_sessions.all().count()
		self.save()

	def remove_session(self, session):
		self.day_sessions.remove(session)
		self.count = self.day_sessions.all().count()
		self.save()

	def set_final_stats(self):
		self.all_complete = True
		self.total_matches = self.total_matches_day()
		self.total_active_scheduled = self.active_scheduled_matches_in_day()
		self.total_temporary = self.temporary_matches_in_day()
		self.total_complete_scheduled_matches = self.total_complete_scheduled_matches_func()
		self.total_complete_reading_count = self.total_complete_reading()
		
		if self.total_active_scheduled != 0:
			percent_i = (self.total_complete_scheduled_matches/self.total_active_scheduled) * 100
			self.percent_successful = percent_i


		self.save()

	def total_matches_day(self):
		count = 0
		for session in self.day_sessions.all():
			matches = session.all_attendance_records()
			matches_count = matches.count()
			count = count+ matches_count

		return count

	def active_scheduled_matches_in_day(self):  
		count= 0
		for session in self.day_sessions.all():
			matches = session.scheduled_attendance_records()
			matches_count = matches.count()
			count = count+ matches_count
		# print("final count", count)
		return count

	def temporary_matches_in_day(self):  
		count= 0
		for session in self.day_sessions.all():
			matches = session.temporary_attendance_records()
			matches_count = matches.count()
			count = count+ matches_count
		# print("final count", count)
		return count 

	def total_complete_scheduled_matches_func(self):
		count= 0
		for session in self.day_sessions.all():
			matches = session.successful_sch_matches()
			matches_count = matches.count()
			count = count+ matches_count
		# print("total_complete_scheduled_matches final count", count)
		return count 

	def total_complete_reading(self):
		count= 0
		for session in self.day_sessions.all():
			ses_count = session.number_successful_matches()
			count = count + ses_count
		# print("total_complete_reading final count", count)
		return count 


	def percent_successful_matches_str(self):
		if self.total_active_scheduled != 0:
			str_for_return = str(self.percent_successful) + " %"
		else:  
			str_for_return = "Not Calculated"
			
		return str_for_return

	def short_day_name(self):
		str_for_return= ""
		str_for_return = self.day.short_name + " - " + str(self.date.month) +"/" + str(self.date.day)
		
		return str_for_return 

	class Meta:
		ordering = ['date',]
		verbose_name = 'Day With Daily Sessions'
		verbose_name_plural = 'Days With Daily Sessions'

	def __str__(self):
		return self.day.name + " - " + str(self.date.month) +"/" + str(self.date.day)+"/" + str(self.date.year)

#Profiles

def image_upload_location(instance, filename, **kwargs):
	file_path = 'profile_images/{filename}'.format(filename=filename) 
	return file_path

class Student_Profile(models.Model):
	user = models.OneToOneField(CustomUser, related_name="student_profile",
									on_delete=models.CASCADE)
	match_needed = models.BooleanField(default=False)
	age = models.IntegerField(null=True, blank=True, max_length=None)
	gender = models.ForeignKey(Gender, related_name="student_gender",
								 on_delete=models.CASCADE ,null=True, blank=True)
	school = models.ForeignKey(School, related_name="student_school",
								 on_delete=models.CASCADE ,null=True, blank=True)
	grade = models.ForeignKey(Grade, related_name="student_grade",
								 on_delete=models.CASCADE ,null=True, blank=True)
	primary_lang = models.ForeignKey(Language, related_name="student_primary_lang",
								 on_delete=models.CASCADE ,null=True, blank=True)
	secondary_lang = models.ForeignKey(Language, related_name="student_secondary_lang",
								 on_delete=models.CASCADE ,null=True, blank=True)
	contact_person = models.CharField(max_length=255, null=True, blank=True)
	contact_relationship = models.CharField(max_length=255, null=True, blank=True)
	contact_number = models.CharField(max_length=255, null=True, blank=True,)
	available_day_time_slots = models.ManyToManyField(Session_Day_Time,
							related_name="student_preferred_schedule", blank=True,) 
	scheduled_day_time_slots = models.ManyToManyField(Session_Day_Time,
							related_name="student_scheduled_slots", blank=True,)
	comment = models.TextField(max_length=1000, null=True, blank=True,)
	profile_notes = models.ManyToManyField(Note, related_name="student_profile_notes",
					blank=True,)
	image = models.ImageField(verbose_name="Photo", upload_to=image_upload_location,
							null=True, blank=True)		
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user']
		verbose_name = 'Student Profile'
		verbose_name_plural = 'Student Profiles'

	def __str__(self):
		return self.user.full_name

@receiver(post_delete, sender=Student_Profile)
def stu_image_submission_delete(sender, instance, **kwargs):
	instance.image.delete(False)

class Volunteer_Profile(models.Model):
	user = models.OneToOneField(CustomUser, related_name="volunteer_profile",
								on_delete=models.CASCADE)
	match_needed = models.BooleanField(default=False)
	gender = models.ForeignKey(Gender, related_name="volunteer_gender",
								 on_delete=models.CASCADE ,null=True, blank=True)
	primary_lang = models.ForeignKey(Language, related_name="vol_primary_lang",
								 on_delete=models.CASCADE ,null=True, blank=True)
	secondary_lang = models.ForeignKey(Language, related_name="vol_secondary_lang",
								 on_delete=models.CASCADE ,null=True, blank=True)
	in_school = models.BooleanField(default=False)
	highest_completed = models.TextField(max_length=1000, null=True, blank=True,)
	contact_number = models.CharField(max_length=255, null=True, blank=True,)
	available_day_time_slots = models.ManyToManyField(Session_Day_Time,
							related_name="volunteer_preferred_schedule", blank=True,) 
	scheduled_day_time_slots = models.ManyToManyField(Session_Day_Time,
							related_name="volunteer_scheduled_slots", blank=True,)	
	comment = models.TextField(max_length=1000, null=True, blank=True,)
	profile_notes = models.ManyToManyField(Note, related_name="volunteer_profile_notes",
					blank=True,)
	image = models.ImageField(verbose_name="Photo", upload_to=image_upload_location,
							null=True, blank=True)

	mega= models.ForeignKey(Mega_Team, related_name="vol_mega_team",
									on_delete=models.SET_NULL, null=True, blank=True,)

	team = models.ForeignKey(Team, related_name="vol_team",
									on_delete=models.SET_NULL, null=True, blank=True,)

	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user']
		verbose_name = 'Volunteer Profile'
		verbose_name_plural = 'Volunteer Profiles'

	def __str__(self):
		return self.user.full_name

@receiver(post_delete, sender=Volunteer_Profile)
def vol_image_submission_delete(sender, instance, **kwargs):
	instance.image.delete(False)

class Staff_Profile(models.Model):
	user = models.OneToOneField(CustomUser, related_name="staff_profile",
								on_delete=models.CASCADE)
	gender = models.ForeignKey(Gender, related_name="staff_gender",
								 on_delete=models.CASCADE ,null=True, blank=True)
	primary_lang = models.ForeignKey(Language, related_name="staff_primary_lang",
								 on_delete=models.CASCADE ,null=True, blank=True)
	secondary_lang = models.ForeignKey(Language, related_name="staff_secondary_lang",
								 on_delete=models.CASCADE ,null=True, blank=True)
	contact_number = models.CharField(max_length=255, null=True, blank=True)
	comment = models.TextField(max_length=1000, null=True, blank=True,)
	profile_notes = models.ManyToManyField(Note, related_name="staff_profile_notes",
					blank=True,)
	image = models.ImageField(verbose_name="Photo", upload_to=image_upload_location,
					 null=True, blank=True)	
	mega= models.ForeignKey(Mega_Team, related_name="staff_mega_team",
									on_delete=models.SET_NULL, null=True, blank=True,)

	team = models.ForeignKey(Team, related_name="staff_team",
									on_delete=models.SET_NULL, null=True, blank=True,)

	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user']
		verbose_name = 'Staff Profile'
		verbose_name_plural = 'Staff Profiles'

	def __str__(self):
		return self.user.full_name

@receiver(post_delete, sender=Staff_Profile)
def sta_image_submission_delete(sender, instance, **kwargs):
	instance.image.delete(False)

class User_Log(models.Model):
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	date =  models.DateField(null=True, blank=True)
	room =  models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='room_name', verbose_name="Jitsi Room",
							null=True, blank=True)
	time_in =  models.DateTimeField()
	time_out = models.DateTimeField(null=True, blank=True)
	duration_seconds = models.IntegerField(max_length=None, null=True, blank=True, verbose_name="Duration(seconds)")
	logged_in = models.BooleanField(default=False)
	processed = models.BooleanField(default=False)
	complete_log = models.BooleanField(default=False)
	count_in_total = models.BooleanField(default=False)
	day_of_week = models.CharField(max_length=255, null=True, blank=True)
	day_good = models.BooleanField(default=False)
	during_jitsi_open = models.BooleanField(default=False)
	time_in_jitsi_open = models.BooleanField(default=False)
	time_out_jitsi_open = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	needs_attention = models.BooleanField(default=False)
	room_good = models.BooleanField(default=False)
	count_in_total = models.BooleanField(default=False)
	processed_completely = models.BooleanField(default=False)
	manually_added = models.BooleanField(default=False)

	def __str__(self):
		return self.user.full_name

	def local_time_in_only(self):
		# time = self.time_in.time()
		time_local = timezone.localtime(self.time_in).time()
		return time_local

	def local_time_out_only(self):
		# time = self.time_out.time()
		if self.time_out:
			time_local = timezone.localtime(self.time_out).time()
		else:
			time_local = "-"
		return time_local

	def local_time_in_only_str(self):
		# time = self.time_in.time()
		if timezone.localtime(self.time_in).time():
			time_local = timezone.localtime(self.time_in).time()
			string_time = time_local.strftime('%I:%M %p') 
		else:
			string_time ="None"
		return string_time

	def local_time_out_only_str(self):

		if timezone.localtime(self.time_out).time():
			time_local = timezone.localtime(self.time_out).time()
			string_time = time_local.strftime('%I:%M %p') 
		else:
			string_time ="None"
		return string_time

	def minute_str(self):
		if self.duration_seconds:
			if self.duration_seconds < 60:
				minute_str = "<1" 
			else:
				
				minute_str = str(round(self.duration_seconds/60, 1))
			
		else:
			minute_str = "N/A"

		return minute_str

	class Meta:
		verbose_name = 'User Log'
		verbose_name_plural = 'User Logs'

# Reading Levels
class Reading_Level(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		ordering = ['name']
		verbose_name = 'Reading Level'
		verbose_name_plural = 'Reading Levels'

	def __str__(self):
		return self.name



# Student Progress 
class Session_Reading_Level(models.Model):
	date =  models.DateField(null=True, blank=True)
	session = models.ForeignKey(Daily_Session, on_delete=models.CASCADE,
							 related_name='session_rl', null=True, blank=True)
	user = models.ForeignKey(CustomUser, related_name="student_rl",
								on_delete=models.CASCADE)
	level = models.ForeignKey(Reading_Level, related_name="today_level",
								 on_delete=models.CASCADE ,null=True, blank=True)
	level_notes = models.ManyToManyField(Note, related_name="session_level_notes",
					blank=True,)
	updated_by = models.ForeignKey(CustomUser, related_name="updated_by_user",
								on_delete=models.CASCADE, null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user', 'session__date', 'session__day_time']
		verbose_name = 'Session Reading Level Assessment'
		verbose_name_plural = 'Session Reading Level Assessments'

	def __str__(self):
		return self.user.full_name + " - " + self.session.date_session_slot()

class Student_Assessment(models.Model):
	user = models.ForeignKey(CustomUser, related_name="assessments",
								on_delete=models.CASCADE)
	date =  models.DateField(null=True, blank=True)
	assessed_by = models.ForeignKey(CustomUser, related_name="performed_by",
								 on_delete=models.CASCADE ,null=True, blank=True)

	level = models.ForeignKey(Reading_Level, related_name="student_level",
								 on_delete=models.CASCADE ,null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user']
		verbose_name = 'Student Assessment'
		verbose_name_plural = 'Student Assessments'

	def __str__(self):
		return self.user.full_name + " - " + self.level.name

class Student_Progress(models.Model):
	user = models.OneToOneField(CustomUser, related_name="student_progress",
								on_delete=models.CASCADE)
	initial_assessment = models.BooleanField(default=False)
	half_assessment = models.BooleanField(default=False)
	end_assessment = models.BooleanField(default=False)
	last_assessed = models.DateField(null=True, blank=True)
	starting = models.ForeignKey(Reading_Level, related_name="start_level",
								 on_delete=models.CASCADE ,null=True, blank=True)
	current = models.ForeignKey(Reading_Level, related_name="current_level",
								 on_delete=models.CASCADE ,null=True, blank=True)
	end = models.ForeignKey(Reading_Level, related_name="end_level",
								 on_delete=models.CASCADE ,null=True, blank=True)
	assessments = models.ManyToManyField(Student_Assessment, related_name="reading_assessments",
					blank=True,)
	level_progress = models.ManyToManyField(Session_Reading_Level, related_name="reading_progress",
					blank=True,)
	progress_notes = models.ManyToManyField(Note, related_name="student_progress_notes",
					blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user']
		verbose_name = 'Student Progress'
		verbose_name_plural = 'Student Progress'

	def __str__(self):
		return self.user.full_name

class Student_Report(models.Model):
	user = models.OneToOneField(CustomUser, related_name="student_attendance_report", on_delete=models.CASCADE)
	semester = models.ForeignKey(Semester, related_name="student_semester_report", on_delete=models.CASCADE)
	no_logs = models.BooleanField(default=True)
	total_sign_ins = models.IntegerField(max_length=None, null=True, blank=True)
	has_active_match = models.BooleanField(default=False)
	total_active_matches = models.IntegerField(max_length=None, null=True, blank=True)
	total_inactive_matches = models.IntegerField(max_length=None, null=True, blank=True)
	total_scheduled_sessions = models.IntegerField(max_length=None, null=True, blank=True)
	scheduled_semester_hours = models.DecimalField(max_length=None, max_digits=10, decimal_places=1, null=True, blank=True, default=0)
	total_semester_hours = models.DecimalField(max_length=None, max_digits=10, decimal_places=1, null=True, blank=True, default=0)
	semester_pending_hours = models.DecimalField(max_length=None, max_digits=10, decimal_places=1, null=True, blank=True, default=0)
	semester_breakout_hours = models.DecimalField(max_length=None, max_digits=10, decimal_places=1, null=True, blank=True, default=0)
	sessions_scheduled = models.ManyToManyField(Daily_Session,
									 related_name="student_scheduled_sessions",
									 blank=True,)
	scheduled_count = models.IntegerField(max_length=None, null=True, blank=True)
	attended_count = models.IntegerField(max_length=None, null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	note = models.TextField(max_length=1000, blank=True, null=True)
	total_temp_matches = models.IntegerField(max_length=None, null=True, blank=True, default=0)
	temporary_buddies = models.ManyToManyField(CustomUser,
									 related_name="student_temp_buddies",
									 blank=True,)

	class Meta:
		ordering = ['user__full_name']
		verbose_name = 'Student Report'
		verbose_name_plural = 'Student Reports'

	def __str__(self):
		return self.user.full_name + "Report"

	def complete_sessions(self):
		complete = self.sessions_scheduled.filter(date__lte=timezone.now())
		return complete

class Volunteer_Report(models.Model):
	user = models.OneToOneField(CustomUser, related_name="volunteer_attendance_report", on_delete=models.CASCADE)
	semester = models.ForeignKey(Semester, related_name="volunteer_semester_report", on_delete=models.CASCADE)
	no_logs = models.BooleanField(default=True)
	total_sign_ins = models.IntegerField(max_length=None, null=True, blank=True)
	has_active_match = models.BooleanField(default=False)
	total_active_matches = models.IntegerField(max_length=None, null=True, blank=True)
	total_inactive_matches = models.IntegerField(max_length=None, null=True, blank=True)
	total_scheduled_sessions = models.IntegerField(max_length=None, null=True, blank=True)
	total_semester_hours = models.DecimalField(max_length=None, max_digits=10, decimal_places=1, null=True, blank=True, default=0)
	sessions_scheduled = models.ManyToManyField(Daily_Session,
									 related_name="volunteer_scheduled_sessions",
									 blank=True,)
	scheduled_count = models.IntegerField(max_length=None, null=True, blank=True)
	attended_count = models.IntegerField(max_length=None, null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	total_temp_matches = models.IntegerField(max_length=None, null=True, blank=True, default=0)
	temporary_buddies = models.ManyToManyField(CustomUser,
									 related_name="vol_temp_buddies",
									 blank=True,)

	class Meta:
		ordering = ['user__full_name']
		verbose_name = 'Volunteer Report'
		verbose_name_plural = 'Volunteer Reports'

	def __str__(self):
		return self.user.full_name + "Report"

class Attendance_Status(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Attendance Status'
		verbose_name_plural = 'Attendance Statuses'

	def __str__(self):
		return self.name

class Sign_In_By_Day(models.Model):
	user = models.ForeignKey(CustomUser, related_name="sign_ins", on_delete=models.CASCADE)
	day = models.ForeignKey(Day_With_Daily_Session, related_name="day_with_session", on_delete=models.CASCADE) 
	session = models.ForeignKey(Daily_Session, related_name="sch_session", on_delete=models.CASCADE,
									null=True, blank=True) 
	scheduled = models.BooleanField(default=False)
	signed_in = models.BooleanField(default=False)
	status = models.ForeignKey(Attendance_Status, null=True, blank=True, related_name="session_time_status", on_delete=models.CASCADE)
	excused = models.BooleanField(default=False)
	meet_with_sheduled = models.BooleanField(default=False)
	temp_match_created = models.BooleanField(default=False)
	temporary_buddies = models.ManyToManyField(CustomUser,
									 related_name="user_temp_buddies",
									 blank=True,)
	session_slot = models.ForeignKey(Session_Day_Time, null=True, blank=True, related_name="slot", on_delete=models.CASCADE)
	total_sign_ins = models.IntegerField(max_length=None, null=True, blank=True)
	logs = models.ManyToManyField(User_Log, related_name="user_log", blank=True)
	pending_minutes = models.IntegerField(max_length=None, null=True, blank=True, default=0)
	breakout_minutes = models.IntegerField(max_length=None, null=True, blank=True,  default=0)
	meeting_minutes = models.IntegerField(max_length=None, null=True, blank=True,  default=0)
	total_minutes = models.IntegerField(max_length=None, null=True, blank=True,  default=0)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user__full_name', 'day__date']
		verbose_name = 'User Sign In By Day'
		verbose_name_plural = 'User Sign Ins By Day'

	def __str__(self):
		return str(self.day)

	def calculate_total_minutes(self):
		pending_type = Room_Type.objects.get(letter="P")
		breakout_type = Room_Type.objects.get(letter="B")
		meeting_type = Room_Type.objects.get(letter="M")

		total_seconds = 0
		pending_seconds = 0
		breakout_seconds = 0
		meeting_seconds = 0

		for log in self.logs.all():
			if log.duration_seconds:
				total_seconds = total_seconds + log.duration_seconds
				if log.room.room_type == pending_type:
					pending_seconds = pending_seconds + log.duration_seconds
				elif log.room.room_type == breakout_type:
					breakout_seconds = breakout_seconds + log.duration_seconds
				elif log.room.room_type == meeting_type:
					meeting_seconds = meeting_seconds + log.duration_seconds


		total_minutes = math.ceil(total_seconds/60)
		pending_minutes = math.floor(pending_seconds/60)
		breakout_minutes = math.ceil(breakout_seconds/60)
		meeting_minutes = math.ceil(meeting_seconds/60)

		self.total_minutes = total_minutes
		self.pending_minutes = pending_minutes
		self.breakout_minutes = breakout_minutes
		self.meeting_minutes = meeting_minutes
		self.save()



class Team_Meeting(models.Model):
	team = models.OneToOneField(Team, related_name="meeting", on_delete=models.CASCADE)
	day = models.ForeignKey(Day, on_delete=models.CASCADE ,null=False, blank=False) 
	time = models.TimeField(blank=True, null=True)

	class Meta:
		ordering = ['id',]
		verbose_name = 'Team Meeting'
		verbose_name_plural = 'Team Meetings'

	def __str__(self):
		return str(self.team) + " Meeting"

	

class Day_With_Team_Meeting(models.Model):
	date = models.DateField(verbose_name="Date", unique=True)
	day = models.ForeignKey(Day, on_delete=models.CASCADE ,null=False, blank=False) 
	semester =  models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='semester_meetings', null=True, blank=True)
	day_meetings = models.ManyToManyField(Team_Meeting,
									 related_name="day_meetings",
									 blank=True,)
	
	count = models.IntegerField(default = 0)

	class Meta:
		ordering = ['date',]
		verbose_name = 'Day With Team Meeting'
		verbose_name_plural = 'Day With Team Meetings'

	def __str__(self):
		return self.day.name + " - " + str(self.date.month) +"/" + str(self.date.day)+"/" + str(self.date.year)

	

class Day_With_Orientation_Meeting(models.Model):
	date = models.DateField(verbose_name="Date", unique=True)
	time_start = models.TimeField(blank=True, null=True)
	time_end = models.TimeField(blank=True, null=True)
	allowed_participants = models.ManyToManyField(CustomUser, related_name="orientation_allowed", blank=True)

	class Meta:
		ordering = ['date',]
		verbose_name = 'Day With Orientation Meeting'
		verbose_name_plural = 'Day With Orientation Meetings'

	def __str__(self):
		return str(self.date.month) +"/" + str(self.date.day)+"/" + str(self.date.year)


class Sign_In_By_User(models.Model):
	user = models.OneToOneField(CustomUser, related_name="user_sign_ins", on_delete=models.CASCADE)
	completely_done = models.BooleanField(default=False)
	total_sign_ins = models.IntegerField(max_length=None, null=True, blank=True)
	diff_count = models.IntegerField(max_length=None, null=True, blank=True)
	logs = models.ManyToManyField(User_Log, related_name="user_logs", blank=True)
	good_day_logs = models.ManyToManyField(User_Log, related_name="logs_good_day", blank=True)
	missing_time_logs = models.ManyToManyField(User_Log, related_name="logs_missing_time", blank=True)
	missing_time_good_logs = models.ManyToManyField(User_Log, related_name="logs_missing_time_good_day", blank=True)
	total_minutes = models.IntegerField(max_length=None, null=True, blank=True,  default=0)
	total_hours = models.IntegerField(max_length=None, null=True, blank=True,  default=0)
	total_sign_ins_4_8 = models.IntegerField(max_length=None, null=True, blank=True)
	logs_4_8 = models.ManyToManyField(User_Log, related_name="user_logs_4_8", blank=True)
	total_minutes_4_8 = models.IntegerField(max_length=None, null=True, blank=True,  default=0)
	total_hours_4_8 = models.IntegerField(max_length=None, null=True, blank=True,  default=0)
	missing_out = models.BooleanField(default=False)
	missing_out_good_day = models.BooleanField(default=False)
	problem_user = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	explore_user_logs = models.BooleanField(default=False)
	total_minutes_good = models.IntegerField(max_length=None, null=True, blank=True,  default=0)
	total_hours_good = models.IntegerField(max_length=None, null=True, blank=True,  default=0)

	class Meta:
		ordering = ['user__full_name']
		verbose_name = 'Sign In By User'
		verbose_name_plural = 'Sign Ins By User'

	def __str__(self):
		return str(self.user)

	def calculate_total_minutes(self):
		total_seconds = 0

		for log in self.logs.all():
			if log.duration_seconds:
				total_seconds = total_seconds + log.duration_seconds
		total_minutes = math.ceil(total_seconds/60)


		self.total_minutes = total_minutes
		total_hours = math.ceil(total_minutes/60)
		self.total_hours = total_hours
		print("Total Hours", self.user, self.total_hours)

		g_total_seconds = 0

		for log in self.good_day_logs.all():
			if log.duration_seconds:
				g_total_seconds = g_total_seconds + log.duration_seconds
		g_total_minutes = math.ceil(g_total_seconds/60)


		self.total_minutes_good = g_total_minutes
		g_total_hours = math.ceil(g_total_minutes/60)
		self.total_hours_good = g_total_hours

		print("Good Total Hours", self.user, self.total_hours_good)

		self.save()






