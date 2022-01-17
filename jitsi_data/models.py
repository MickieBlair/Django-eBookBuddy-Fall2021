from django.db import models
from users.models import CustomUser, Role
from site_admin.models import Room

# Create your models here.

class Jitsi_ID(models.Model):
	jitsi_id = models.CharField(max_length=255, null=True, blank=True)
	in_room = models.BooleanField(default=False, verbose_name="In Room")
	room =  models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='id_room_name', verbose_name="Jitsi Room",
							null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['room']
		verbose_name = 'Jitsi ID'
		verbose_name_plural = 'Jitsi IDs'

	def __str__(self):
		return self.room.name  + " ID"



class Jitsi_User_Status(models.Model):
	user = models.OneToOneField(CustomUser, related_name="status_jitsi", on_delete=models.CASCADE)
	# jitsi_id = models.CharField(max_length=255, null=True, blank=True)
	jitsi_ids = models.ManyToManyField(Jitsi_ID, related_name="ids_jitsi", blank=True,)	
	online = models.BooleanField(default=False, verbose_name="Online")
	room =  models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='jitsi_room_name', verbose_name="Jitsi Room",
							null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	class Meta:
		ordering = ['user']
		verbose_name = 'Jitsi User Status'
		verbose_name_plural = 'Jitsi User Status'

	def __str__(self):
		return self.user.full_name  + " Jitsi Status"


class Jitsi_Websocket_Error(models.Model):
	file = models.CharField(max_length=255, null=True, blank=True)
	function_name = models.CharField(max_length=255, null=True, blank=True)
	location_in_function = models.CharField(max_length=255, null=True, blank=True)		
	occurred_for_user = models.CharField(max_length=255, null=True, blank=True)
	error_text = models.TextField(max_length=2000, null=True, blank=True)
	created	= models.DateTimeField(verbose_name='created', auto_now_add=True)

	class Meta:
		ordering = ['-created']
		verbose_name = 'Error'
		verbose_name_plural = 'Errors'

	def __str__(self):
		return self.function_name

class Jitsi_Meeting_Room(models.Model):
	room = models.OneToOneField(Room, related_name="room_jitsi", on_delete=models.CASCADE)
	occupied = models.BooleanField(default=False)
	count = models.IntegerField(verbose_name="Count", default=0)
	student_alone = models.BooleanField(default=False)
	mismatch = models.BooleanField(default=False)
	participants = models.ManyToManyField(CustomUser, related_name="api_participants", blank=True,)	
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def in_room(self):
		return self.participants.all()

	def add_participant(self, user):
		self.participants.add(user)
		if self.participants.all().count() == 0:
			self.count = 0
			self.occupied = False
		else:
			self.count = self.participants.all().count()
			self.occupied = True

		self.save()
		return self.participants.all()

	def remove_participant(self, user):
		print("before remove", self.participants.all())
		self.participants.remove(user)
		if self.participants.all().count() == 0:
			self.count = 0
			self.occupied = False
		else:
			self.count = self.participants.all().count()
			self.occupied = True

		self.save()

		
		print("after remove", self.participants.all())
		return self.participants.all()

	def get_count(self):
		if self.participants.all().count() == 0:
			self.count = 0
			self.occupied = False
		else:
			self.count = self.participants.all().count()
			self.occupied = True
		self.save()

	def check_student_alone_mismatch(self):

		staff_present = False
		volunteer_present = False
		student_present = False
		print("staff_present", staff_present)
		print("volunteer_present", volunteer_present)
		print('student_present', student_present)

		for part in self.participants.all():
			if part.role.name == "Staff":
				staff_present = True
				print("staff_present", staff_present)
			elif part.role.name == "Volunteer":
				volunteer_present = True
				print("volunteer_present", volunteer_present)
			elif part.role.name == "Student":
				student_present =True
				print('student_present', student_present)

		if student_present:
			 if staff_present or volunteer_present:
			 	self.student_alone = False
			 	print("student_alone is False")
			 else:
			 	self.student_alone = True
			 	print("student_alone is True")

		else:
			self.student_alone = False
			print("student_alone is False")

		j_room_parts = list(self.participants.all().order_by('username'))
		r_room_parts = list(self.room.participants.all().order_by('username'))

		print("j_room", j_room_parts)
		print("r_room", r_room_parts)

		if j_room_parts == r_room_parts:
			print("Equal participant")
			self.mismatch = False

		else:
			print("Mismatch participants")
			self.mismatch = True

		self.save()

	class Meta:
		ordering = ['room__id']
		verbose_name = 'Jitsi Meeting Room'
		verbose_name_plural = 'Jitsi Meeting Rooms'

	def __str__(self):
		return self.room.name









