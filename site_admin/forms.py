from django.forms import ModelForm
from django import forms
from site_admin.models import Day, Semester, Session_Day_Time, Daily_Session
from site_admin.models import Student_Profile, Volunteer_Profile, Staff_Profile
from site_admin.models import Room, Upload_CSV

from reading_sessions.models import Scheduled_Match

class CSVBulkUploadForm(forms.ModelForm):
  class Meta:
    model = Upload_CSV
    fields = ('name', 'csv_file',)

class Create_Scheduled_Match_Form(forms.ModelForm):
	class Meta:
		model = Scheduled_Match
		fields='__all__'

	def clean(self):
		semester = self.cleaned_data['semester']
		student = self.cleaned_data['student']
		existing = Scheduled_Match.objects.filter(student=student, semester=semester, match_active=True)
		if existing.count() > 0:
			raise forms.ValidationError("Student has existing active match.\nOnly one active match allowed per semester.")

class Edit_Scheduled_Match_Form(forms.ModelForm):
	class Meta:
		model = Scheduled_Match
		fields=('scheduled_slots', )

class Create_Semester_Form(forms.ModelForm):
	class Meta:
		model = Semester
		fields='__all__'

	def clean_active_semester(self):
		active_semester = self.cleaned_data['active_semester']
		if Semester.objects.exclude(pk=self.instance.pk).filter(active_semester=True).exists():
			if active_semester:				
				active_semester = Semester.objects.get(active_semester=True)
				msg1 = "Only One Active Semester Can Exist."
				msg2 = active_semester.name + " is already set as active."
				self.add_error('active_semester', msg1)
				self.add_error('active_semester', msg2)
			else:
				return active_semester
		else:
			return active_semester

class Edit_Semester_Form(forms.ModelForm):
	class Meta:
		model = Semester
		fields=('name','start_date','end_date','active_semester' )

class Create_Session_Day_Time_Form(forms.ModelForm):
	class Meta:
		model = Session_Day_Time
		fields='__all__'

	def clean(self):
		session_slot = self.cleaned_data['session_slot']
		session_slot = session_slot.upper()
		day = self.cleaned_data['day']

		if Session_Day_Time.objects.exclude(pk=self.instance.pk).filter(day=day, session_slot=session_slot).exists():
			msg = "Session Slot - " + session_slot + " for " + day.name + " is already in use."
			self.add_error('session_slot', msg)
		else:
			self.cleaned_data['session_slot'] = session_slot
			return self.cleaned_data 


class Edit_Student_Profile_Form(forms.ModelForm):
	class Meta:
		model = Student_Profile
		fields='__all__'

class Edit_Volunteer_Profile_Form(forms.ModelForm):
	class Meta:
		model = Volunteer_Profile
		fields='__all__'

class Edit_Staff_Profile_Form(forms.ModelForm):
	class Meta:
		model = Staff_Profile
		fields='__all__'


class Breakout_Rooms_Form(forms.Form):
	number_of_rooms = forms.IntegerField(label='Number of Rooms')
	
	def clean_number_of_rooms(self):
		number_of_rooms = self.cleaned_data['number_of_rooms']
		print("number_of_rooms", number_of_rooms)
		if number_of_rooms == "":
			raise forms.ValidationError("This field is required.")
		elif number_of_rooms < 1:
			raise forms.ValidationError("Number must be greater than 0.")


class Create_Room_Form(forms.ModelForm):
	class Meta:
		model = Room
		fields='__all__'