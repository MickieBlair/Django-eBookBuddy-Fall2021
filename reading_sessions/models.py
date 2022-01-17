from django.db import models
from users.models import CustomUser, Role
from site_admin.models import Semester, Session_Day_Time
from site_admin.models import Note, Room, Daily_Session, Reading_Level
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
import datetime

class Connection_Drop(models.Model):
	user = models.ForeignKey(CustomUser, related_name="drop_status", on_delete=models.CASCADE)
	room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='drop_room_location', null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['-date_created']
		verbose_name = 'Connection Drop'
		verbose_name_plural = 'Connection Drops'

	def __str__(self):
		return self.user.full_name  + ": Drops"


class Match_Type(models.Model):
	name = models.CharField(max_length=255, unique=True)
	short_name = models.CharField(max_length=255, unique=True)
	class Meta:
		verbose_name = 'Match Type'
		verbose_name_plural = 'Match Types'

	def __str__(self):
		return self.name

class Temporary_Match_Type(models.Model):
	name = models.CharField(max_length=255, unique=True)
	short_name = models.CharField(max_length=255, unique=True)
	class Meta:
		verbose_name = 'Temporary Match Type'
		verbose_name_plural = 'Temporary Match Types'

	def __str__(self):
		return self.name

class Scheduled_Match(models.Model):
	semester =  models.ForeignKey(Semester, on_delete=models.CASCADE,
								related_name='scheduled_match_semester',
								null=False, blank=False)
	student = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='match_student',
								null=False, blank=False)
	volunteer = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
								related_name='match_volunteer',
								null=False, blank=False)
	match_active = models.BooleanField(default=True)
	scheduled_slots = models.ManyToManyField(Session_Day_Time,
										related_name="match_slots", blank=True,)	
	sessions_scheduled = models.ManyToManyField(Daily_Session,
									 related_name="scheduled_matches_in_session",
									 blank=True,)
	notes = models.ManyToManyField(Note,related_name="scheduled_match_notes", blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def __str__(self):
		string_for_return = ""
		if self.student:
			string_for_return ="Student: " + self.student.username
		else:
			string_for_return = "No Student"

		if self.volunteer:
			string_for_return = string_for_return + " - Volunteer: " + self.volunteer.username
		else:
			string_for_return = string_for_return + " - No Volunteer"
		return string_for_return

	def status_text(self):
		text = ""
		if self.match_active:
			text = "Active"
		else:
			text = "Inactive"

		return text

	def active_scheduled_matches_in_semester(semester):
		matches = Scheduled_Match.objects.filter(semester = semester, match_active=True)
		return matches

	def inactive_scheduled_matches_in_semester(semester):
		matches = Scheduled_Match.objects.filter(semester = semester, match_active=False)
		return matches

	def all_scheduled_matches_in_semester(semester):
		matches = Scheduled_Match.objects.filter(semester = semester)
		return matches

	class Meta:
		verbose_name = 'Scheduled Match'
		verbose_name_plural = 'Scheduled Matches'

def post_save_remove_match_needed_status_receiver(sender, instance, *args, **kwargs):
	if instance.match_active:
		instance.student.student_profile.match_needed = False
		instance.student.student_profile.save()
		instance.volunteer.volunteer_profile.match_needed = False
		instance.volunteer.volunteer_profile.save()
		# instance.student.student_session_status.regular_match = instance.volunteer
		# instance.student.student_session_status.save()
		# instance.volunteer.volunteer_session_status.regular_match = instance.student
		# instance.volunteer.volunteer_session_status.save()

	else:
		instance.student.student_profile.match_needed = True
		instance.student.student_profile.save()
		instance.volunteer.volunteer_profile.match_needed = True
		instance.volunteer.volunteer_profile.save()
		# instance.student.student_session_status.regular_match = None
		# instance.student.student_session_status.save()
		# instance.volunteer.volunteer_session_status.regular_match = None
		# instance.volunteer.volunteer_session_status.save()

post_save.connect(post_save_remove_match_needed_status_receiver, sender=Scheduled_Match)

@receiver(post_delete, sender=Scheduled_Match)
def adjust_users_need_match(sender, instance, **kwargs):
	print("\n\n\n\nPost Delete", instance)
	try:		
		instance.student.student_profile.match_needed = True
		instance.student.student_profile.scheduled_day_time_slots.clear()
		instance.student.student_profile.save()
		instance.student.session_status.current_active_match_type = None
		instance.student.session_status.scheduled_buddy = None
		instance.student.session_status.save()

		reading_level_assessments = instance.student.student_rl.all()

		for level in reading_level_assessments:
			level.delete()

		
		instance.volunteer.volunteer_profile.match_needed = True
		instance.volunteer.volunteer_profile.scheduled_day_time_slots.clear()
		instance.volunteer.volunteer_profile.save()
		instance.volunteer.session_status.current_active_match_type = None
		instance.volunteer.session_status.scheduled_match = None
		instance.volunteer.session_status.scheduled_buddy = None
		instance.volunteer.session_status.save()

	except Exception as e:
		print(e, instance.student, instance.volunteer)

	
	# if instance.student.student_session_status:
	# 	instance.student.student_session_status.regular_match = None
	# 	instance.student.student_session_status.save()
	# if instance.volunteer.volunteer_session_status:
	# 	instance.volunteer.volunteer_session_status.regular_match = None
	# 	instance.volunteer.volunteer_session_status.save()

	# for session in instance.sessions_scheduled.all():
	# 	log = Attendance_Log.objects.get(session=session, content_object=instance.attendance_record.id)
	# 	log.delete()

class Temporary_Match(models.Model):
	session = models.ForeignKey(Daily_Session, on_delete=models.CASCADE,
							 related_name='temporary_match_session', null=True, blank=True)
	temp_type = models.ForeignKey(Temporary_Match_Type, on_delete=models.CASCADE,
					related_name='temp_type_match', null=True, blank=True)	
	student_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
									 related_name='student_temp_match', null=True, blank=True)
	teacher_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
										 related_name='teacher_temp_match', null=True, blank=True)
	match_active = models.BooleanField(default=True)
	created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='temp_match',
									null=True, blank=True)
	notes = models.ManyToManyField(Note,related_name="temporary_match_notes", blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def __str__(self):
		string_for_return = ""
		if self.student_user:
			string_for_return ="Student: " + self.student_user.username
		else:
			string_for_return = "No Student"

		if self.teacher_user:
			string_for_return = string_for_return + " - " + self.teacher_user.role.name + ": " + self.teacher_user.username
		else:
			string_for_return = string_for_return + " - No Volunteer"
		return string_for_return

	class Meta:
		verbose_name = 'Temporary Match'
		verbose_name_plural = 'Temporary Matches'


def post_save_new_temporary_match_receiver(sender, instance, created, **kwargs):
	pass
	# match_type = Match_Type.objects.get(name="Temporary")
	# if created:
	# 	match_status = Match_Status.objects.create(session=instance.session,
	# 												match_type=match_type,
	# 												temp_match=instance)

	# temp_match_status = Temporary_Match_Status.objects.get_or_create(temp_match=instance)

	# if created:
	# 	attendance_record = Temporary_Session_Attendance_Record.objects.create(match=instance,
	# 															session=instance.session,
	# 															student_present = True,
	# 															volunteer_present=True,
	# 															)
post_save.connect(post_save_new_temporary_match_receiver, sender=Temporary_Match)



class User_Session_Status(models.Model):
	user = models.OneToOneField(CustomUser, related_name="session_status", on_delete=models.CASCADE)
	manual_redirect_on = models.BooleanField(default=False)
	orientation_complete = models.BooleanField(default=False)
	logged_in = models.BooleanField(default=False)
	on_landing_page = models.BooleanField(default=False)
	needs_new_buddy = models.BooleanField(default=False, verbose_name="Needs New Buddy")
	current_active_match_type = models.ForeignKey(Match_Type, on_delete=models.SET_NULL,
					related_name='current_type_active', null=True, blank=True,
					verbose_name = "Type Active")
	scheduled_match = models.ForeignKey(Scheduled_Match, on_delete=models.SET_NULL,
					related_name="sch_match", null=True, blank=True)

	temp_match = models.ForeignKey(Temporary_Match, on_delete=models.SET_NULL,
					related_name="temp_match", null=True, blank=True)

	needs_session_match = models.BooleanField(verbose_name="Needs Match", default=False)

	room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='room_location', null=True, blank=True)

	scheduled_buddy = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sch_buddy',
										null=True, blank=True)

	in_room_with_sch_buddy = models.BooleanField(verbose_name="With Sch Buddy", default=False)

	temporary_buddy = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='temp_buddy',
										null=True, blank=True)

	in_room_with_temp_buddy = models.BooleanField(verbose_name="With Temp Buddy", default=False)

	# in_room = models.BooleanField(default=False)
	# in_session_today = models.BooleanField(verbose_name="In Session Today", default=False)
	# in_session_slot = models.CharField(max_length=1, null= True, blank=True)

	# scheduled_session_slot = models.CharField(max_length=1, null= True, blank=True)
	# 
	# in_room_with_match = models.BooleanField(verbose_name="With Match", default=False)

	# with_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="buddy_in_room",
	# 							null=True, blank=True)

	# comment = models.TextField(max_length=1000, null=True, blank=True,)
	# status_notes = models.ManyToManyField(Note, related_name="user_status_notes", blank=True,)

	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user']
		verbose_name = 'User Session Status'
		verbose_name_plural = 'User Session Statuses'

	def __str__(self):
		return self.user.full_name  + ": User Session Status"

def pre_save_user_session_status_receiver(sender, instance, **kwargs):
	pass
	# print("\n\n\n\n\nSAVING", instance.user, instance.manual_redirect_on)

pre_save.connect(pre_save_user_session_status_receiver, sender=User_Session_Status)


class Match_Status_Option(models.Model):
	name = models.CharField(max_length=255, unique=True)
	class Meta:
		verbose_name = 'Match Status Option'
		verbose_name_plural = 'Match Status Option'

	def __str__(self):
		return self.name

class Match_Status(models.Model):
	match_status_active = models.BooleanField(default=True, verbose_name="Active")
	session = models.ForeignKey(Daily_Session, on_delete=models.CASCADE,
					related_name='match_status_session', null=True, blank=True)
	match_type = models.ForeignKey(Match_Type, on_delete=models.CASCADE,
					related_name='match_status_type', null=True, blank=True)	
	sch_match = models.ForeignKey(Scheduled_Match,
										related_name="sch_match_status",
										on_delete=models.CASCADE, null=True, blank = True)


	member_reassigned = models.BooleanField(default=False, verbose_name="M-R")
	vol_reassigned = models.BooleanField(default=False, verbose_name="V-R")
	student_reassigned = models.BooleanField(default=False, verbose_name="S-R")

	temp_match = models.ForeignKey(Temporary_Match,
										related_name="temp_match_status",
										on_delete=models.CASCADE, null=True, blank = True)
	
	student_online = models.BooleanField(default=False, verbose_name="Student Online")
	display_student_location = models.BooleanField(default=True)
	buddy_online = models.BooleanField(default=False, verbose_name="Buddy Online")
	display_buddy_location = models.BooleanField(default=True)
	both_online = models.BooleanField(default=False, verbose_name="Both Present")
	room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='match_location', null=True, blank=True)
	status = models.ForeignKey(Match_Status_Option, related_name="status_option",
									on_delete=models.CASCADE, null=True, blank = True)
	match_status_notes = models.ManyToManyField(Note, related_name="match_status_notes", blank=True,)

	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['session__date', 'session__day_time', 'both_online']
		verbose_name = 'Match Status'
		verbose_name_plural = 'Match Statuses'




	def get_type(self):
		if self.match_type.name == "Scheduled":
			return self.match_type.short_name	
		else:
			if self.match_type.name == "Temporary":
				return self.match_type.short_name[0] + ":" + self.temp_match.temp_type.short_name

	def get_student(self):
		if self.match_type.name == "Scheduled":
			return self.sch_match.student	
		else:
			if self.match_type.name == "Temporary":
				return self.temp_match.student_user

	def get_buddy(self):
		if self.match_type.name == "Scheduled":
			return self.sch_match.volunteer	
		else:
			if self.match_type.name == "Temporary":
				return self.temp_match.teacher_user

	def string_for_return(self):
		if self.match_type.name == "Scheduled":
			return self.match_type.name	 + " - " + str(self.sch_match)		
		else:
			if self.match_type.name == "Temporary":
				return self.match_type.name + " - " + self.temp_match.temp_type.name + " - " + str(self.temp_match)	


	def __str__(self):
		return self.string_for_return()



class Match_Attendance_Record(models.Model):
	session = models.ForeignKey(Daily_Session, on_delete=models.CASCADE,
					related_name='match_attendance_session', null=True, blank=True)
	match_type = models.ForeignKey(Match_Type, on_delete=models.CASCADE,
					related_name='match_attendance_type', null=True, blank=True)

	sch_match = models.ForeignKey(Scheduled_Match, related_name="sch_match_attendance_record",
							on_delete=models.CASCADE,  null=True, blank=True)

	member_reassigned = models.BooleanField(default=False, verbose_name="M-R")

	temp_match = models.ForeignKey(Temporary_Match, related_name="temp_match_attendance_record",
							on_delete=models.CASCADE,  null=True, blank=True)
	

	student_present = models.BooleanField(default=False, verbose_name="S-Present")
	student_time_in = models.TimeField(null=True, blank=True)
	student_time_out = models.TimeField(null=True, blank=True)
	student_reassigned = models.BooleanField(default=False, verbose_name="S-R")
	student_time_in_pending = models.IntegerField(null=True, blank=True, default=0)
	student_time_in_breakout = models.IntegerField(null=True, blank=True, default=0)

	volunteer_present = models.BooleanField(default=False, verbose_name="V-Present")
	volunteer_time_in = models.TimeField(null=True, blank=True)
	volunteer_time_out = models.TimeField(null=True, blank=True)
	volunteer_reassigned = models.BooleanField(default=False, verbose_name="V-R")
	volunteer_in_breakout_alone = models.IntegerField(null=True, blank=True, default=0)
	volunteer_in_breakout_w_student = models.IntegerField(null=True, blank=True, default=0)

	match_complete_at = models.TimeField(null=True, blank=True)
	match_ended_at = models.TimeField(null=True, blank=True)
	duration = models.DurationField(null=True, blank=True)
	match_successful = models.BooleanField(default=False, verbose_name="Success")

	status = models.ForeignKey(Match_Status_Option, related_name="record_status",
									on_delete=models.CASCADE, null=True, blank = True)

	notes = models.ManyToManyField(Note,related_name="match_attendance_notes", blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")


	class Meta:
		ordering = ['session__date', 'session__day_time']
		verbose_name = 'Match Attendance Record'
		verbose_name_plural = 'Match Attendance Records'

	def string_for_return(self):
		if self.match_type.name == "Scheduled":
			return self.match_type.name	 + " - " + str(self.sch_match)		
		else:
			if self.match_type.name == "Temporary":
				return self.match_type.name + " - " + self.temp_match.temp_type.name + " - " + str(self.temp_match)	

	def get_type(self):
		if self.match_type.name == "Scheduled":
			return self.match_type.short_name	
		else:
			if self.match_type.name == "Temporary":
				return self.match_type.short_name[0] + ": " + self.temp_match.temp_type.short_name

	def get_student(self):
		if self.match_type.name == "Scheduled":
			return self.sch_match.student	
		else:
			if self.match_type.name == "Temporary":
				return self.temp_match.student_user

	def get_buddy(self):
		if self.match_type.name == "Scheduled":
			return self.sch_match.volunteer	
		else:
			if self.match_type.name == "Temporary":
				return self.temp_match.teacher_user
				



	def __str__(self):
		return self.string_for_return()

	# def get_reassigned_status_notes(self):
	# 	reassigned_category = Note_Category.objects.get(name="Reassigned Status")
	# 	reassigned_notes = Note.objects.filter(category = reassigned_category)
	# 	return reassigned_notes


	# def calculate_duration(self):
	# 	if self.match_complete_at and self.match_ended_at:
	# 		self.duration = self.match_ended_at - self.match_complete_at
	# 	self.save()

def pre_save_attendance_receiver(sender, instance, *args, **kwargs):
	print("Pre Save Match Attendance", instance.student_reassigned, instance.volunteer_reassigned)
	if instance.student_reassigned and instance.volunteer_reassigned:
		instance.status = Match_Status_Option.objects.get(name="Both Reassigned")

	elif instance.student_reassigned and not instance.volunteer_reassigned:
		instance.status = Match_Status_Option.objects.get(name="Student Reassigned")

	elif not instance.student_reassigned and instance.volunteer_reassigned:
		instance.status = Match_Status_Option.objects.get(name="Volunteer Reassigned")

	else:
		instance.status = None

	if not instance.member_reassigned:
		if instance.student_present and instance.volunteer_present:
			instance.match_successful= True 
		else:
			instance.match_successful = False


pre_save.connect(pre_save_attendance_receiver, sender=Match_Attendance_Record)

def post_save_duration_receiver(sender, instance, *args, **kwargs):
	pass
	# print("Post Save")
	# if instance.duration == None:
	# instance.calculate_duration()

post_save.connect(post_save_duration_receiver, sender=Match_Attendance_Record)

class Arrival_Description(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Arrival Description'
		verbose_name_plural = 'Arrival Descriptions'

	def __str__(self):
		return self.name

class Follow_Up_Type(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Follow Up Type'
		verbose_name_plural = 'Follow Up Types'

	def __str__(self):
		return self.name

class Relational_Engagement(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False, unique=True)
	desc = models.CharField(max_length=255, null=True, blank=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Relational Engagement'
		verbose_name_plural = 'Relational Engagements'

	def __str__(self):
		return self.name

class Evaluation_Level(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False, unique=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Evaluation Level'
		verbose_name_plural = 'Evaluation Levels'

	def __str__(self):
		return self.name


class End_Session_Evaluation(models.Model):
	date =  models.DateField(null=True, blank=True)
	completed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
										 related_name='user_completed_by', null=True, blank=True)
	read_with_scheduled = models.BooleanField(verbose_name="Read With Scheduled", null=True, blank=True)
	scheduled_student = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
									 related_name='evalution_for_scheduled', null=True, blank=True)
	scheduled_student_attendance = models.ForeignKey(Arrival_Description, on_delete=models.CASCADE,
									 related_name='sch_arrival', null=True, blank=True)


	temp_student_assigned = models.BooleanField(verbose_name="Temporary Student Assigned", null=True, blank=True)

	level_assessment_performed = models.BooleanField(default=False, verbose_name="Performed Assessment")
	assessment_level = models.ForeignKey(Reading_Level,related_name='assessed_level', on_delete=models.CASCADE, null=True, blank=True)
	
	
	scheduled_sub = models.BooleanField(default=False, verbose_name="Scheduled Sub")
	
	
	
	temp_student = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
									 related_name='evalution_for_other', null=True, blank=True)
	temp_student_attendance = models.ForeignKey(Arrival_Description, on_delete=models.CASCADE,
									 related_name='other_arrival', null=True, blank=True)
	books_read = models.IntegerField(max_length=None, null=True, blank=True)
	no_books = models.BooleanField(default=False, verbose_name="No Books Read")
	level_today = models.ManyToManyField(Reading_Level,related_name='session_levels', blank=True)

	engagement = models.ForeignKey(Relational_Engagement, on_delete=models.CASCADE,
									 related_name='relational_engagemnet', null=True,
									 blank=True, verbose_name="Relational Engagement")
	word_recognition = models.ForeignKey(Evaluation_Level, on_delete=models.CASCADE,
									 related_name='word_rec', null=True, blank=True,
									 verbose_name="Word Recognition")
	pronunciation_fluency = models.ForeignKey(Evaluation_Level, on_delete=models.CASCADE,
									 related_name='pro_flu', null=True, blank=True,
									 verbose_name="Pronunciation/Fluency")
	vocabulary = models.ForeignKey(Evaluation_Level, on_delete=models.CASCADE,
									 related_name='voc', null=True, blank=True,
									 verbose_name="Vocabulary")

	comprehension = models.ForeignKey(Evaluation_Level, on_delete=models.CASCADE,
									 related_name='comp', null=True, blank=True,
									 verbose_name="Comprehension")

	tbd = models.ForeignKey(Evaluation_Level, on_delete=models.CASCADE,
									 related_name='tbd_unk', null=True, blank=True,
									 verbose_name="TBD")

	session_comment = models.TextField(max_length=2000, blank=True, null=True)
	social_emotional_learning_comment = models.TextField(max_length=2000, blank=True, null=True)
	follow_up_needed = models.BooleanField(default=False, verbose_name="Needs Follow Up")
	follow_up_type = models.ForeignKey(Follow_Up_Type, on_delete=models.CASCADE,
									 related_name='type_follow_up', null=True, blank=True)
	follow_up_comment = models.TextField(max_length=2000, blank=True, null=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	
	class Meta:
		ordering = ['-date']
		verbose_name = 'End Session Evaluation'
		verbose_name_plural = 'End Session Evaluations'

	def get_student(self):
		student = None
		if self.read_with_scheduled:
			if self.scheduled_student:
				student =  self.scheduled_student
			else:
				student =  None
		else:
			if self.temp_student:
				student =  self.temp_student 
			else:
				student =  None

		return student

	def get_level_read_str(self):
		str_for_return = ""
		if self.level_today.all().count() == 1:
			str_for_return = self.level_today.all().first().name
		elif self.level_today.all().count() == 0:
			str_for_return = ""		
		else:
			for level in self.level_today.all():
				if level == self.level_today.all().last():
					str_for_return = str_for_return + level.name
				else: 
					str_for_return = str_for_return + level.name + " - "



		return str_for_return

	def string_for_return(self):
		if self.completed_by and self.temp_student:			
			str_for_return = self.completed_by.full_name + " for " + self.temp_student.full_name 
		elif self.completed_by and self.scheduled_student:			
			str_for_return = self.completed_by.full_name + " for " + self.scheduled_student.full_name
		else:			
			str_for_return = self.completed_by.full_name
		return str_for_return

	def __str__(self):
		# return self.string_for_return()
		return str(self.id)

def pre_save_evaluation(sender, instance, *args, **kwargs):
	if not instance.read_with_scheduled:
		instance.scheduled_student = None 
	if instance.books_read == 0:
		instance.no_books = True
	else:
		instance.no_books = False

pre_save.connect(pre_save_evaluation, sender=End_Session_Evaluation)

class Incomplete_Evaluation(models.Model):
	evaluation = models.ForeignKey(End_Session_Evaluation, on_delete=models.CASCADE,
										 related_name='incomplete', null=True, blank=True)
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
										 related_name='incompletes', null=True, blank=True)
	reason = models.CharField(max_length=255, null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'Incomplete Evaluation'
		verbose_name_plural = 'Incomplete Evaluations'

	def __str__(self):
		return self.user.full_name  + "- Incomplete"



class API_Jitsi_Room_Participants(models.Model):
	room = models.OneToOneField(Room, on_delete=models.CASCADE, 
							related_name='jitis_room')
	participants = models.ManyToManyField(CustomUser,
					related_name="api_room_participants", blank=True,)
	occupied = models.BooleanField(default=False)
	api_count =  models.IntegerField(verbose_name="Count", default=0)
	
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['id']
		verbose_name = 'API Room Participants'
		verbose_name_plural = 'API Room Participants'

	def in_room(self):
		return self.participants.all()

	def add_participant(self, user):
		self.participants.add(user)
		if self.participants.all().count() == 0:
			self.api_count = 0
			self.occupied = False
		else:
			self.api_count = self.participants.all().count()
			self.occupied = True
		self.save()
		# print("ADDED", self.num_participants)
		return self.participants.all()

	def remove_participant(self,user):
		self.participants.remove(user)
		if self.participants.all().count() == 0:
			self.api_count = 0
			self.occupied = False
		else:
			self.api_count = self.participants.all().count()
			self.occupied = True
		self.save()
		# print("REMOVED", self.num_participants)
		return self.participants.all()

	def get_count(self):
		if self.participants.all().count() == 0:
			self.api_count = 0
			self.occupied = False
		else:
			self.api_count = self.participants.all().count()
			self.occupied = True
		self.save()

	def __str__(self):
		return self.room.name + " Participants"


class A_Problem_User(models.Model):
	user = models.ForeignKey(CustomUser, related_name="connection_problem", on_delete=models.CASCADE)
	room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='problem_location', null=True, blank=True)
	date =  models.DateField(null=True, blank=True)
	comment = models.TextField(max_length=1000, null=True, blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['-date_created', 'user__username']
		verbose_name = 'A_Problem_User'
		verbose_name_plural = 'A_Problem_User'

	def __str__(self):
		return self.user.full_name  + ": Can't Connect"

def pre_save_problem_user_receiver(sender, instance, *args, **kwargs):
	today = timezone.localtime(timezone.now()).date()
	instance.date = today

pre_save.connect(pre_save_problem_user_receiver, sender=A_Problem_User)


class Status_Redirect(models.Model):
	user_to_redirect = models.OneToOneField(CustomUser,
							related_name='status_redirect',
							on_delete=models.CASCADE , unique=True)

	to_room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='to_location', null=True, blank=True)
	auto_send = models.BooleanField(default=False)

	created_by = models.ForeignKey(CustomUser, related_name='created_user',
									on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.user_to_redirect.username

	class Meta:
		verbose_name = 'Status Redirect'
		verbose_name_plural = 'Status Redirects'


def pre_save_status_redirect_receiver(sender, instance, *args, **kwargs):
	instance.user_to_redirect.status_ws.has_status_redirect = True
	instance.user_to_redirect.status_ws.save()
	

pre_save.connect(pre_save_status_redirect_receiver, sender=Status_Redirect)


class User_Status(models.Model):
	user = models.OneToOneField(CustomUser, related_name="status_ws", on_delete=models.CASCADE)
	online = models.BooleanField(default=False, verbose_name="Online")
	in_room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='status_location', null=True, blank=True)
	all_connected = models.BooleanField(default=False, verbose_name="All Connected")
	max_reached = models.BooleanField(default=False, verbose_name="Max Reached")
	has_ws_redirect = models.BooleanField(default=False, verbose_name="WS Redirect")
	has_status_redirect = models.BooleanField(default=False, verbose_name="Status Redirect")
	needs_to_reenter = models.BooleanField(default=False, verbose_name="Needs To Reenter")
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user']
		verbose_name = 'A_User_Status'
		verbose_name_plural = 'A_User_Status'

	def __str__(self):
		return self.user.full_name  + " Status"


def pre_save_status_ws(sender, instance, *args, **kwargs):
	print("Instance online", instance.online)
	# if not instance.online:
		# instance.all_connected = False
		# instance.in_room = None
		# instance.max_reached = False

pre_save.connect(pre_save_status_ws, sender=User_Status)








