from django.forms import ModelForm
from django import forms
from reading_sessions.models import End_Session_Evaluation

# date =  models.DateField(null=True, blank=True)
# 	completed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
# 										 related_name='user_completed_by', null=True, blank=True)
# 	read_with_scheduled = models.BooleanField(verbose_name="Read With Scheduled", null=True, blank=True)
# 	scheduled_student = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
# 									 related_name='evalution_for_scheduled', null=True, blank=True)
# 	scheduled_student_attendance = models.ForeignKey(Arrival_Description, on_delete=models.CASCADE,
# 									 related_name='sch_arrival', null=True, blank=True)


# 	temp_student_assigned = models.BooleanField(verbose_name="Temporary Student Assigned", null=True, blank=True)

# 	level_assessment_performed = models.BooleanField(default=False, verbose_name="Performed Assessment")
# 	assessment_level = models.ForeignKey(Reading_Level,related_name='assessed_level', on_delete=models.CASCADE, null=True, blank=True)
	
	
# 	scheduled_sub = models.BooleanField(default=False, verbose_name="Scheduled Sub")
	
	
	
# 	temp_student = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
# 									 related_name='evalution_for_other', null=True, blank=True)
# 	temp_student_attendance = models.ForeignKey(Arrival_Description, on_delete=models.CASCADE,
# 									 related_name='other_arrival', null=True, blank=True)
# 	books_read = models.IntegerField(max_length=None, null=True, blank=True)
# 	no_books = models.BooleanField(default=False, verbose_name="No Books Read")
# 	level_today = models.ManyToManyField(Reading_Level,related_name='session_levels', blank=True)

# 	engagement = models.ForeignKey(Relational_Engagement, on_delete=models.CASCADE,
# 									 related_name='relational_engagemnet', null=True,
# 									 blank=True, verbose_name="Relational Engagement")
# 	word_recognition = models.ForeignKey(Evaluation_Level, on_delete=models.CASCADE,
# 									 related_name='word_rec', null=True, blank=True,
# 									 verbose_name="Word Recognition")
# 	pronunciation_fluency = models.ForeignKey(Evaluation_Level, on_delete=models.CASCADE,
# 									 related_name='pro_flu', null=True, blank=True,
# 									 verbose_name="Pronunciation/Fluency")
# 	vocabulary = models.ForeignKey(Evaluation_Level, on_delete=models.CASCADE,
# 									 related_name='voc', null=True, blank=True,
# 									 verbose_name="Vocabulary")

# 	comprehension = models.ForeignKey(Evaluation_Level, on_delete=models.CASCADE,
# 									 related_name='comp', null=True, blank=True,
# 									 verbose_name="Comprehension")

# 	tbd = models.ForeignKey(Evaluation_Level, on_delete=models.CASCADE,
# 									 related_name='tbd_unk', null=True, blank=True,
# 									 verbose_name="TBD")

# 	session_comment = models.TextField(max_length=2000, blank=True, null=True)
# 	social_emotional_learning_comment = models.TextField(max_length=2000, blank=True, null=True)
# 	follow_up_needed = models.BooleanField(default=False, verbose_name="Needs Follow Up")
# 	follow_up_type = models.ForeignKey(Follow_Up_Type, on_delete=models.CASCADE,
# 									 related_name='type_follow_up', null=True, blank=True)
# 	follow_up_comment = models.TextField(max_length=2000, blank=True, null=True)
# 	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
# 	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

class Link_End_Session_Evaluation_Form(forms.ModelForm):
	# date = forms.DateField(widget = forms.SelectDateWidget)
	# CHOICES = [('True', 'Yes'), ('False', 'No')]
	# read_with_scheduled = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
	
	class Meta:
		model = End_Session_Evaluation
		fields='__all__'
		# fields=('completed_by', 'date', 'read_with_scheduled')

	def clean(self):
		print("\n\n\n\n\n\nCleaning Link Form", self.cleaned_data)
		date = self.cleaned_data['date']
		read_with_scheduled = self.cleaned_data['read_with_scheduled']

		if not date:
			self.add_error('date', "This field is required.")

		if not read_with_scheduled:
			self.add_error('read_with_scheduled', "This field is required.")



		return self.cleaned_data

class End_Session_Evaluation_Form(forms.ModelForm):
	class Meta:
		model = End_Session_Evaluation
		fields='__all__'

	def clean(self):
		print("\n\n\n\n\n\nCleaning", self.cleaned_data)

		# read_with_scheduled = self.cleaned_data['read_with_scheduled']
		# print("read_with_scheduled", read_with_scheduled)
		# if read_with_scheduled == None:
		# 	raise forms.ValidationError({'read_with_scheduled': ["This field is required.",]})

		# else:
		# 	if read_with_scheduled:
		# 		print("Student", self.cleaned_data['scheduled_student'])
		# 		print("read with read_with_scheduled")				
		# 		scheduled_student_attendance = self.cleaned_data['scheduled_student_attendance']
		# 		if scheduled_student_attendance == None:
		# 			print("NO scheduled_student_attendance")
		# 			raise forms.ValidationError({'scheduled_student_attendance': ["This field is required.",]})
		# 	else:
		# 		print("did not read with scheduled")
		# 		self.cleaned_data['scheduled_student'] = None
		# 		self.cleaned_data['read_with_scheduled'] = False
		# 		temp_student_assigned = self.cleaned_data['temp_student_assigned']
		# 		if temp_student_assigned:
		# 			print("temp_student_assigned YES")
		# 			temp_student = self.cleaned_data['temp_student']
		# 			if temp_student == None:
		# 				raise forms.ValidationError({'temp_student': ["This field is required.",]})
		# 		else:
		# 			print("temp_student_assigned NO")


		# level_assessment_performed = self.cleaned_data['level_assessment_performed']
		# if level_assessment_performed:
		# 	assessment_level = self.cleaned_data['assessment_level']
		# 	if assessment_level == None:
		# 		self.add_error('assessment_level', "This field is required.")
				# raise forms.ValidationError("This field is required.")
		# number_of_rooms = self.cleaned_data['number_of_rooms']
		# print("number_of_rooms", number_of_rooms)
		# if number_of_rooms == "":
		# 	raise forms.ValidationError("This field is required.")
		# elif number_of_rooms < 1:
		# 	raise forms.ValidationError("Number must be greater than 0.")

		return self.cleaned_data

class In_Process_End_Session_Evaluation_Form(forms.ModelForm):
	class Meta:
		model = End_Session_Evaluation
		fields='__all__'

	def clean(self):
		print("\n\n\n\n\n\nCleaning")

		for key,value in self.cleaned_data.items():
			print("Item", key, ':', value)

		read_with_scheduled = self.cleaned_data['read_with_scheduled']

		if read_with_scheduled == None:
			raise forms.ValidationError({'read_with_scheduled': ["This field is required.",]})
		elif read_with_scheduled:
			print("READ WITH SCHEDULED")
			self.cleaned_data['read_with_scheduled'] = True

			scheduled_student = self.cleaned_data['scheduled_student']

			scheduled_student_attendance = self.cleaned_data['scheduled_student_attendance']
			if scheduled_student_attendance == None:
				raise forms.ValidationError({'scheduled_student_attendance': ["This field is required.",]})

			
		else:
			print("DID NOT READ WITH SCHEDULED")
			self.cleaned_data['read_with_scheduled'] = False
			temp_student_assigned = self.cleaned_data['temp_student_assigned']
			if temp_student_assigned == None:
				raise forms.ValidationError({'temp_student_assigned': ["This field is required.",]})
			elif temp_student_assigned:
				self.cleaned_data['temp_student_assigned'] = True
				temp_student = self.cleaned_data['temp_student']
				if temp_student == None:
					raise forms.ValidationError({'temp_student': ["This field is required.",]})
			else:
				self.cleaned_data['temp_student_assigned'] = False



		# raise forms.ValidationError({'follow_up_type': ["This field is required.",]})

		level_assessment_performed = self.cleaned_data['level_assessment_performed']
		if level_assessment_performed:
			assessment_level = self.cleaned_data['assessment_level']
			if assessment_level == None:
				raise forms.ValidationError({'assessment_level': ["This field is required.",]})

		books_read = self.cleaned_data['books_read']

		if books_read != 0:
			level_today = self.cleaned_data['level_today']
			if level_today.count() == 0:
				raise forms.ValidationError({'level_today': ["This field is required when the number of books read is greater than 0",]})


		follow_up_needed = self.cleaned_data['follow_up_needed']
		if follow_up_needed:
			follow_up_type = self.cleaned_data['follow_up_type']
			if follow_up_type == None:
				raise forms.ValidationError({'follow_up_type': ["This field is required.",]})




		print("\nAfter Cleaning")

		for key,value in self.cleaned_data.items():
			print("Item", key, ':', value)

		return self.cleaned_data


		


		# number_of_rooms = self.cleaned_data['number_of_rooms']
		# print("number_of_rooms", number_of_rooms)
		# if number_of_rooms == "":
		# 	raise forms.ValidationError("This field is required.")
		# elif number_of_rooms < 1:
		# 	raise forms.ValidationError("Number must be greater than 0.")

		