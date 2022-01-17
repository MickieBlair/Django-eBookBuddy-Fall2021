from channels.db import database_sync_to_async
import json
from django.db.models import Q
from django.utils import timezone
from users.models import CustomUser
from site_admin.models import Room, User_Log, Note, Room_Type
from site_admin.models import Daily_Session
from reading_sessions.models import User_Session_Status, Match_Status, Match_Status_Option
from reading_sessions.models import Scheduled_Match, Temporary_Match
from reading_sessions.models import Match_Type, Temporary_Match_Type
from websockets.models import Websocket_Error, Socket_Group, Redirect
from websockets.models import PrivateChatRoom, RoomChatMessage, UnreadChatRoomMessages
from websockets.models import User_Private_Room_List, Help_Request
from websockets.serializers import LazyRoomParticipantsEncoder, LazyPrivateRoomEncoder
from websockets.serializers import LazyRedirectEncoder, LazyHelpEncoder
from websockets.serializers import LazySessionStatusEncoder, LazyMatchStatusEncoder
from websockets.match_constants import *

def localtime_now_date():
	date_now = timezone.localtime(timezone.now()).date()
	return date_now

def localtime_now():
	date_time_now = timezone.localtime(timezone.now())
	return date_time_now

from channels.db import database_sync_to_async
import json
from django.db.models import Q
from django.utils import timezone
from users.models import CustomUser
from site_admin.models import Room, User_Log, Note, Room_Type
from site_admin.models import Daily_Session
from reading_sessions.models import User_Session_Status, Match_Status, Match_Status_Option
from reading_sessions.models import Scheduled_Match, Temporary_Match
from reading_sessions.models import Match_Type, Temporary_Match_Type
from websockets.models import Websocket_Error, Socket_Group, Redirect
from websockets.models import PrivateChatRoom, RoomChatMessage, UnreadChatRoomMessages
from websockets.models import User_Private_Room_List, Help_Request
from websockets.serializers import LazyRoomParticipantsEncoder, LazyPrivateRoomEncoder
from websockets.serializers import LazyRedirectEncoder, LazyHelpEncoder
from websockets.serializers import LazySessionStatusEncoder, LazyMatchStatusEncoder
from websockets.match_constants import *

@database_sync_to_async
def get_room_by_location(user, location_id):
	try:
		room = Room.objects.get(slug=location_id)

	except Exception as e:
		print("BROKEN get_room_by_location", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="get_room_by_location",
						location_in_function="try block for getting room",
						occurred_for_user=user.username,
						error_text=e)
	return room

def set_match_status_status_on_temp_match(match_status):
	try:
		inactive = Match_Status_Option.objects.get(name="Match Inactive")
		match_status.status = inactive
		match_status.save()
	# print("End Match Status Status", match_status.id, match_status.status)
	except Exception as e:
		print("BROKEN set_match_status_status_on_temp_match", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="set_match_status_status_on_temp_match",
						location_in_function="set_match_status_status_on_temp_match",
						occurred_for_user="match status" + str(match_status.id),
						error_text=str(e))


	


def set_match_status_status(match_status):
	try:
		if match_status.member_reassigned:
			if match_status.vol_reassigned and match_status.student_reassigned:
				match_status.status = VR_SR
			elif not match_status.vol_reassigned and match_status.student_reassigned:
				match_status.status = SR
			elif match_status.vol_reassigned and not match_status.student_reassigned:
				match_status.status = VR
		match_status.save()

		# if match_status.match_type == "Scheduled":
		# 	noteSR = Note_Category.objects.get(group_name="Scheduled Match", name="Student Reassigned")
		# 	noteVR = Note_Category.objects.get(group_name="Scheduled Match", name="Student Reassigned")
		# 	noteVRSR = Note_Category.objects.get(group_name="Scheduled Match", name="Both Reassigned")
		


		# print("End Match Status Status", match_status.id, match_status.status)
	except Exception as e:
		print("BROKEN set_match_status_status", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="set_match_status_status",
						location_in_function="set_match_status_status",
						occurred_for_user="match status" + str(match_status.id),
						error_text=str(e))
	
	

def adjust_user_session_status_for_temporary_match(temp_match_ini, user_ini):
	try:
		user = CustomUser.objects.get(id=user_ini.id)
		temp_match = Temporary_Match.objects.get(id=temp_match_ini.id)
		user.session_status.current_active_match_type = TEMP_TYPE
		user.session_status.temp_match=temp_match
		if user.role == STUDENT_ROLE:
			user.session_status.temporary_buddy = temp_match.teacher_user
			user.session_status.needs_session_match = False
		elif user.role == VOLUNTEER_ROLE:
			user.session_status.temporary_buddy = temp_match.student_user
			user.session_status.needs_session_match = False
		
		user.session_status.save()
		# print("IN ADJUSTING FOR TEMP MATCH", user, user.session_status.current_active_match_type)
		# print("IN ADJUSTING FOR TEMP MATCH", user, user.session_status.needs_session_match)
	except Exception as e:
		print("EXCEPTION adjust_user_session_status_for_temporary_match", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="adjust_user_session_status_for_temporary_match",
						location_in_function="adjust_user_session_status_for_temporary_match",
						occurred_for_user=user_ini.username,
						error_text=str(e))

def adjust_user_session_status_for_other_users_in_temporary_match(temp_match):
	try:
		volunteers_original_student = temp_match.teacher_user.session_status.scheduled_buddy
		print("Volunteer's Original Student", volunteers_original_student)
		if volunteers_original_student:
			volunteers_original_student.session_status.needs_new_buddy = True
			volunteers_original_student.session_status.save()

		students_original_volunteer = temp_match.student_user.session_status.scheduled_buddy
		print("Student's Original Volunteer", students_original_volunteer)
		if students_original_volunteer:
			students_original_volunteer.session_status.needs_new_buddy = True
			students_original_volunteer.session_status.save()

	except Exception as e:
		print("EXCEPTION adjust_user_session_status_for_other_users_in_temporary_match", e)

		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="adjust_user_session_status_for_other_users_in_temporary_match",
						location_in_function="try adjust_user_session_status_for_other_users_in_temporary_match for creating temp match",
						occurred_for_user="temp_match" + str(temp_match.id),
						error_text=e)
	
@database_sync_to_async
def create_temporary_match(user, content):
	
	redirect = None
	try:
		print("DB Create temporary match", content)
		sent_by = CustomUser.objects.get(id=content['sent_by'])
		temp_type_match = Temporary_Match_Type.objects.get(id=content['temp_match_type'])
		current_session = Daily_Session.objects.get(id=content['current_session_id'])
		student_user = CustomUser.objects.get(id=content['student_new_match_id'])
		teacher_user = CustomUser.objects.get(id=content['vol_new_match_id'])
		student_user.session_status.current_active_match_type = Match_Type.objects.get(name="Temporary")
		student_user.session_status.save()
		teacher_user.session_status.current_active_match_type = Match_Type.objects.get(name="Temporary")
		teacher_user.session_status.save()

		redirect, created = Redirect.objects.get_or_create(user_to_redirect = student_user)
		redirect.to_user = teacher_user
		redirect.to_room = teacher_user.session_status.room
		redirect.auto_send = True
		redirect.created_by = user
		redirect.save()

		print("\n\n\n\n\n\n\n\n\nREDIRECT Room..", redirect.to_room)

		try:
			
			student_match_status = user_match_status(student_user)

			for status in student_match_status:
				print("Student Status", status.id)
				if status.match_type.name == "Scheduled":
					print("The Original Match Status", status.id)
					status.member_reassigned = True
					status.student_reassigned = True
					status.display_student_location = False
					status.student_online = False
					status.save()
					set_match_status_status(status)
					noteSR = Note_Category.objects.get(group__name="Scheduled Match", name="Student Reassigned")
					content_reassigned = "Student Reassigned"
					note_reassigned= Note.objects.create(category=noteSR, author=sent_by,
											content=content_reassigned)
					status.sch_match.notes.add(note_reassigned)

				elif status.match_type.name == "Temporary":
					status.member_reassigned = True
					status.student_reassigned = True
					status.vol_reassigned = True
					status.student_online = False
					status.buddy_online = False
					status.display_student_location = False
					status.display_buddy_location = False
					status.match_status_active = False					
					status.save()
					status.temp_match.match_active = False
					status.temp_match.save()
					set_match_status_status_on_temp_match(status)
					content_inactive = "Temporary Match Inactive for " + current_session.date_session_slot()
					note_inactive= Note.objects.create(category=TEMP_MATCH_INACTIVE, author=sent_by,
											content=content_inactive)
					status.temp_match.notes.add(note_inactive)



			buddy_match_status = user_match_status(teacher_user)
			for status in buddy_match_status:
				print("Buddy Status", status.id)
				if status.match_type.name == "Scheduled":
					print("The Original Match Status", status.id)
					status.member_reassigned = True
					status.vol_reassigned = True
					status.display_buddy_location = False
					status.buddy_online = False
					status.save()
					set_match_status_status(status)
					noteVR = Note_Category.objects.get(group__name="Scheduled Match", name="Volunteer Reassigned")
					content_reassigned = "Volunteer Reassigned"
					note_reassigned= Note.objects.create(category=noteVR, author=sent_by,
											content=content_reassigned)
					status.sch_match.notes.add(note_reassigned)

				elif status.match_type.name == "Temporary":
					status.member_reassigned = True
					status.student_reassigned = True
					status.vol_reassigned = True
					status.display_student_location = False
					status.display_buddy_location = False
					status.student_online = False
					status.buddy_online = False
					status.match_status_active = False
					status.save()
					status.temp_match.match_active = False
					status.temp_match.save()
					set_match_status_status_on_temp_match(status)
					content_inactive = "Temporary Match Inactive for " + current_session.date_session_slot()
					note_inactive= Note.objects.create(category=TEMP_MATCH_INACTIVE, author=sent_by,
											content=content_inactive)
					status.temp_match.notes.add(note_inactive)


			# if Match_Status.objects.filter(session__date=timezone.now().date(),
			# 					sch_match=student_user.session_status.scheduled_match).exists():

			# 	student_sch_match_status = Match_Status.objects.get(session__date=timezone.now().date(),
			# 										sch_match=student_user.session_status.scheduled_match)
			# 	if student_sch_match_status.match_type.name == "Scheduled":
			# 		print("Student Original Match_Status", student_sch_match_status.id)
			# 		student_sch_match_status.member_reassigned = True
			# 		student_sch_match_status.student_reassigned = True
			# 		student_sch_match_status.display_student_location = False
			# 		student_sch_match_status.save()
			# 		set_match_status_status(student_sch_match_status)
			# 	elif student_sch_match_status.match_type.name == "Temporary":
			# 		print("Student Temporary Match_Status", student_sch_match_status.id)
			# 		student_sch_match_status.member_reassigned = True
			# 		student_sch_match_status.student_reassigned = True
			# 		student_sch_match_status.display_student_location = False
			# 		student_sch_match_status.display_buddy_location = False
			# 		student_sch_match_status.save()
			# 		set_match_status_status_on_temp_match(student_sch_match_status)



			# else:
			# 	print("STUDENT Original Match_Status DoesNotExist")
		except Exception as e:
			print("EXCEPTION, create_temporary_match", e)
			Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="create_temporary_match",
						location_in_function="student_match_status",
						occurred_for_user=user.username,
						error_text=e)

		# try:
		# 	if Match_Status.objects.filter(session__date=timezone.now().date(),
		# 						sch_match=teacher_user.session_status.scheduled_match).exists():

		# 		teacher_sch_match_status = Match_Status.objects.get(session__date=timezone.now().date(),
		# 											sch_match=teacher_user.session_status.scheduled_match)
		# 		if teacher_sch_match_status.match_type.name == "Scheduled":
		# 			print("Teacher Original Match_Status", teacher_sch_match_status.id)
		# 			teacher_sch_match_status.member_reassigned = True
		# 			teacher_sch_match_status.vol_reassigned = True
		# 			teacher_sch_match_status.display_buddy_location = False
		# 			teacher_sch_match_status.save()
		# 			set_match_status_status(teacher_sch_match_status)
		# 		elif teacher_sch_match_status.match_type.name == "Temporary":
		# 			print("Teacher Temporary Match_Status", teacher_sch_match_status.id)
		# 			teacher_sch_match_status.member_reassigned = True
		# 			teacher_sch_match_status.vol_reassigned = True
		# 			teacher_sch_match_status.display_buddy_location = False
		# 			teacher_sch_match_status.display_student_location = False
		# 			teacher_sch_match_status.save()
		# 			set_match_status_status_on_temp_match(teacher_sch_match_status)
		# 	else:
		# 		print("Teacher Original Match_Status DoesNotExist")

		# except Exception as e:
		# 	print("EXCEPTION, getting Original student match_status", e)

		

		# student_sch_match_status = Match_Status.objects.get(session__date=timezone.now().date(),
		# 									sch_match=student_user.session_status.scheduled_match)

		content_created = "Temporary Match Created for " + current_session.date_session_slot()
		# content_inactive = "Temporary Match Inactive for " + current_session.date_session_slot()

		note_created = Note.objects.create(category=TEMP_MATCH_CREATED, author=sent_by,
											content=content_created)
		# note_inactive= Note.objects.create(category=TEMP_MATCH_INACTIVE, author=sent_by,
		# 									content=content_inactive)


		# student_current_temps = Temporary_Match.objects.filter(student_user=student_user,
		# 														match_active=True)
		# for match in student_current_temps:
		# 	match.match_active = False
		# 	match.save()
		# 	match.temp_match_status.match_status_active = False
		# 	match.temp_match_status.save()
		# 	match.notes.add(note_inactive)

		# teacher_current_temps = Temporary_Match.objects.filter(teacher_user=teacher_user,
		# 														match_active=True)
		# for match in student_current_temps:
		# 	match.match_active = teacher_current_temps
		# 	match.save()
		# 	match.temp_match_status.match_status_active = False
		# 	match.temp_match_status.save()
		# 	match.notes.add(note_inactive)

		new_temp_match = Temporary_Match.objects.create(session = current_session,
														temp_type= temp_type_match,
														student_user= student_user,
														teacher_user= teacher_user,
														match_active = True,
														created_by=sent_by)
		new_temp_match.notes.add(note_created)

		match_status = Match_Status.objects.create(session=current_session,
													match_type=TEMP_TYPE,
													temp_match=new_temp_match,
													status=VM_SM)

		adjust_user_session_status_for_temporary_match(new_temp_match, student_user)
		adjust_user_session_status_for_temporary_match(new_temp_match, teacher_user)


		adjust_user_session_status_for_other_users_in_temporary_match(new_temp_match)

		

	except Exception as e:
		print("\n\n\nBROKEN create_temporary_match", e)	
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="create_temporary_match",
						location_in_function="try block for creating temp match",
						occurred_for_user=user.username,
						error_text=e)

	return redirect

def process_status_temporary(match_status_ini, user_ini, joining):
	try:
		user = CustomUser.objects.get(id=user_ini.id)
		match_status = Match_Status.objects.get(id=match_status_ini.id)
		print("\n\n\n\nPROCESSING STATUS", user, match_status, joining)
		student_redirect = None
		# if match_status.match_type == SCH_TYPE:
		# 	print("Scheduled")

		student = match_status.temp_match.student_user
		buddy = match_status.temp_match.teacher_user

		print("Student", student, student.session_status.logged_in)
		print("buddy", buddy, buddy.session_status.logged_in)

		if student.session_status.logged_in:
			match_status.student_online = True
		else:
			match_status.student_online = False



		if buddy.session_status.logged_in:
			match_status.buddy_online = True
		else:
			match_status.buddy_online = False

		print("AFTER Student", student, student.session_status.logged_in)
		print("AFTER buddy", buddy, buddy.session_status.logged_in)


		if not match_status.buddy_online and not match_status.student_online:
			print("Neither Online")
			match_status.both_online = False
			match_status.status = VM_SM

		elif match_status.buddy_online and not match_status.student_online:
			print("Student Missing")
			match_status.both_online = False
			match_status.status = SM

		elif not match_status.buddy_online and match_status.student_online:
			print("Volunteer Missing")
			match_status.both_online = False
			match_status.status = VM

		elif match_status.buddy_online and match_status.student_online:
			print("\n\n\n\n\n\nStudent", match_status.student_online)
			print("buddy", match_status.buddy_online)
			match_status.both_online = True

			print("match_status.both_online", match_status.both_online)

			

			if student.session_status.room and buddy.session_status.room:
				if student.session_status.room == buddy.session_status.room:
					print("In Room")
					match_status.room = buddy.session_status.room
					match_status.status = IR

				else:
					print("Pending")
					match_status.status = PR
					redirect, created = Redirect.objects.get_or_create(user_to_redirect = student)
					redirect.to_user = buddy
					redirect.to_room = buddy.session_status.room
					redirect.auto_send = False
					redirect.created_by = buddy
					redirect.save()
		match_status.save()

		if match_status.status != IR:
			match_status.room = None

		if match_status.status == VM and not student.session_status.manual_redirect_on:
		# if match_status.status == VM:
			print("Volunteer missing")
			if student.session_status.room:
				print("Student Room", student.session_status.room)
				if student.session_status.room.room_type.letter =="B":
					print("The Student is in a breakout room")
					student_redirect, created = Redirect.objects.get_or_create(user_to_redirect = student)
					student_redirect.to_user = None
					student_redirect.to_room = Room.objects.get(room_type__letter ="P")
					student_redirect.auto_send = True
					student_redirect.created_by = buddy
					student_redirect.save()
				else:
					print("Student room type letter", student.session_status.room.room_type.letter)

			else:
				print("Student has no Room", student.session_status.room)


		# elif match_status.match_type == TEMP_TYPE:
		# 	print("MATCH IS TEMP TYPE")
		# else:
		# 	pass

		match_status.save()


	except Exception as e:
		print("EXCEPTION process_status_temporary", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="process_status_temporary",
						location_in_function="try block process_status_temporary",
						occurred_for_user=user_ini.username,
						error_text=str(e))
	

	print("MAKING A NEW REDIRECT IN STUDENT PROCESSING", student_redirect)
	return student_redirect


def process_status_scheduled(match_status_ini, user_ini, joining):
	student_redirect = None
	try:
		user = CustomUser.objects.get(id=user_ini.id)
		match_status = Match_Status.objects.get(id=match_status_ini.id)
		print("\n\n\n\nPROCESSING STATUS", user, match_status, joining)
		
		# if match_status.match_type == SCH_TYPE:
		# 	print("Scheduled")

		student = match_status.sch_match.student
		buddy = match_status.sch_match.volunteer

		if student.session_status.logged_in:
			match_status.student_online = True
		else:
			match_status.student_online = False

		if buddy.session_status.logged_in:
			match_status.buddy_online = True
		else:
			match_status.buddy_online = False


		if not match_status.buddy_online and not match_status.student_online:
			print("Neither Online")
			match_status.both_online = False
			match_status.status = VM_SM

		elif match_status.buddy_online and not match_status.student_online:
			print("Student Missing")
			match_status.both_online = False
			match_status.status = SM

		elif not match_status.buddy_online and match_status.student_online:
			print("Volunteer Missing")
			match_status.both_online = False
			match_status.status = VM

		elif match_status.buddy_online and match_status.student_online:
			match_status.both_online = True

			if student.session_status.room and buddy.session_status.room:
				if student.session_status.room == buddy.session_status.room:
					print("In Room")
					match_status.room = buddy.session_status.room
					match_status.status = IR

				else:
					print("Pending")
					match_status.status = PR
					redirect, created = Redirect.objects.get_or_create(user_to_redirect = student)
					redirect.to_user = buddy
					redirect.to_room = buddy.session_status.room
					redirect.auto_send = False
					redirect.created_by = buddy
					redirect.save()
		match_status.save()

		if match_status.status != IR:
			match_status.room = None

		if match_status.status == VM and not student.session_status.manual_redirect_on:
		# if match_status.status == VM:
			print("Volunteer missing")
			if student.session_status.room:
				print("Student Room", student.session_status.room)
				if student.session_status.room.room_type.letter =="B":
					print("The Student is in a breakout room")
					student_redirect, created = Redirect.objects.get_or_create(user_to_redirect = student)
					student_redirect.to_user = None
					student_redirect.to_room = Room.objects.get(room_type__letter ="P")
					student_redirect.auto_send = True
					student_redirect.created_by = buddy
					student_redirect.save()
				else:
					print("Student room type letter", student.session_status.room.room_type.letter)

			else:
				print("Student has no Room", student.session_status.room)


		# elif match_status.match_type == TEMP_TYPE:
		# 	print("MATCH IS TEMP TYPE")
		# else:
		# 	pass

		match_status.save()
	except Exception as e:
		print("EXCEPTION process_status_scheduled", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="process_status_scheduled",
						location_in_function="try block process_status_scheduled",
						occurred_for_user=user_ini.username,
						error_text=str(e))


	

	print("MAKING A NEW REDIRECT IN STUDENT PROCESSING", student_redirect)
	return student_redirect

def student_processing_temporary(student_ini, room, joining):
	student_redirect = None
	student = CustomUser.objects.get(id = student_ini.id)
	try:
		# student_active_type = "student"

		print("\n\n&&&&&&&&&&Student Session Status Joining", student, room, student.session_status.current_active_match_type)
		# if student.session_status.current_active_match_type == SCH_TYPE:
		print("Temporary")
		if student.session_status.temp_match and student.session_status.temp_match.match_active:			
			if student.session_status.temporary_buddy:
				volunteer = student.session_status.temporary_buddy
				print("Volunteer", volunteer)
				if volunteer.session_status.current_active_match_type == TEMP_TYPE:
					print("Volunteer active is Temporary")

					if joining:
						if volunteer.session_status.logged_in:
							student.session_status.needs_session_match = False
							volunteer.session_status.needs_session_match = False
							volunteer.session_status.save()
						else:
							student.session_status.needs_session_match = True

					else:
						if volunteer.session_status.logged_in:
							volunteer.session_status.needs_session_match = True
							volunteer.session_status.save()
							student.session_status.needs_session_match = False

						else:
							volunteer.session_status.needs_session_match = False
							volunteer.session_status.save()
							student.session_status.needs_session_match = False

			student.session_status.save()

			match_status = Match_Status.objects.get(session__date=localtime_now_date(),
													temp_match = student.session_status.temp_match)
			student_redirect = process_status_temporary(match_status, student, joining)

			

		else:
			if joining:
				student.session_status.needs_session_match = True
			else:
				student.session_status.needs_session_match = False
			student.session_status.save()


	except Exception as e:
		print("STUDENT PROCESSING Temporary Exception", e)
		print("EXCEPTION student_processing_temporary", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="student_processing_temporary",
						location_in_function="try block student_processing_temporary",
						occurred_for_user=student_ini.username,
						error_text=str(e))

	return student_redirect

def student_processing_scheduled(student_ini, room, joining):
	print("\n\n\n\n\n************PROCESSING SCHEDULED!!!!!!!!!!")
	student_redirect = None
	student = CustomUser.objects.get(id = student_ini.id)

	if Match_Status.objects.filter(session__date=localtime_now_date(),
		sch_match = student.session_status.scheduled_match).exists():
		print("\n\n\n\n\n************Yes exists")
		try:
			# student_active_type = "student"
			print("\n\n&&&&&&&&&&Student Session Status Joining", student, room, student.session_status.current_active_match_type)
			print("Scheduled")

			if student.session_status.needs_new_buddy:
				print("Needs New Buddy")
				if joining:
					student.session_status.needs_session_match = True
				else:
					student.session_status.needs_session_match = False

				student.session_status.save()

			else:		
				if student.session_status.scheduled_match:			
					if student.session_status.scheduled_buddy:
						volunteer = student.session_status.scheduled_buddy
						print("Volunteer", volunteer)

						if volunteer.session_status.current_active_match_type == SCH_TYPE:
							if joining:
								if volunteer.session_status.logged_in:
									student.session_status.needs_session_match = False
									volunteer.session_status.needs_session_match = False
									volunteer.session_status.save()
								else:
									student.session_status.needs_session_match = True

							else:
								if volunteer.session_status.logged_in:
									volunteer.session_status.needs_session_match = True
									volunteer.session_status.save()
									student.session_status.needs_session_match = False
								else:
									student.session_status.needs_session_match = False
									volunteer.session_status.needs_session_match = False
									volunteer.session_status.save()
						else:
							if joining:
								student.session_status.needs_session_match = True
							else:
								student.session_status.needs_session_match = False

					student.session_status.save()

					match_status = Match_Status.objects.get(session__date=localtime_now_date(),
															sch_match = student.session_status.scheduled_match)
					student_redirect = process_status_scheduled(match_status, student, joining)

			
		except Exception as e:
			print("STUDENT PROCESSING Exception", e)
			Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
							function_name="student_processing_scheduled",
							location_in_function="try block student_processing_scheduled",
							occurred_for_user=student_ini.username,
							error_text=str(e))
	else:
		print("\n\n\n\n\n************No exists")
		if joining:
			print("JOINING KICK")
			student_redirect = "Kick"
		else:
			print("LEAVING")



	

	return student_redirect

def check_for_sessions_today():
	today = localtime_now_date()
	check_todays_sessions = Daily_Session.objects.filter(date=today)
	reading_session_today = False

	if check_todays_sessions.count() > 0:
		reading_session_today = True
	else:
		reading_session_today = False

	print("\n\n\n\n*********Reading SEssions Today", reading_session_today)

	return reading_session_today

def volunteer_processing_temporary(volunteer_ini, room, joining):
	reading_session_today = check_for_sessions_today()

	volunteer = CustomUser.objects.get(id = volunteer_ini.id)
	student_redirect = None
	try:
		if reading_session_today:
			print("\n\nVolunteer Session Status Joining", volunteer, room, volunteer.session_status.current_active_match_type)
			if volunteer.session_status.current_active_match_type == TEMP_TYPE:
				print("Temporary")
				if volunteer.session_status.temp_match and volunteer.session_status.temp_match.match_active:			
					if volunteer.session_status.temporary_buddy:
						student = volunteer.session_status.temporary_buddy
						print("Student", student)
						if student.session_status.current_active_match_type == TEMP_TYPE:
							if joining:
								if student.session_status.logged_in:
									volunteer.session_status.needs_session_match = False
									student.session_status.needs_session_match = False
									student.session_status.save()

								else:
									volunteer.session_status.needs_session_match = True
									student.session_status.needs_session_match = False
									student.session_status.save()

							else:
								if student.session_status.logged_in:
									student.session_status.needs_session_match = True
									student.session_status.save()
									volunteer.session_status.needs_session_match = False
								else:
									volunteer.session_status.needs_session_match = False
									student.session_status.needs_session_match = False
									student.session_status.save()		

					volunteer.session_status.save()

					match_status = Match_Status.objects.get(session__date=localtime_now_date(),
															temp_match = volunteer.session_status.temp_match)
					student_redirect = process_status_temporary(match_status, volunteer, joining)
				else:
					if joining:
						volunteer.session_status.needs_session_match = True
					else:
						volunteer.session_status.needs_session_match = False
					volunteer.session_status.save()

	except Exception as e:
		print("Volunteer PROCESSING Exception", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="volunteer_processing_temporary",
						location_in_function="try block volunteer_processing_temporary",
						occurred_for_user=volunteer_ini.username,
						error_text=str(e))

	return student_redirect




def volunteer_processing_scheduled(volunteer_ini, room, joining):

	reading_session_today = check_for_sessions_today()

	volunteer = CustomUser.objects.get(id = volunteer_ini.id)
	student_redirect = None
	try:
		if reading_session_today:
			print("\n\nVolunteer Session Status Joining", volunteer, room, volunteer.session_status.current_active_match_type)
			print("Scheduled")
			if volunteer.session_status.needs_new_buddy:
				if joining:
					volunteer.session_status.needs_session_match = True
				else:
					volunteer.session_status.needs_session_match = False
				volunteer.session_status.save()

			else:
				
				if volunteer.session_status.scheduled_match:			
					if volunteer.session_status.scheduled_buddy:
						student = volunteer.session_status.scheduled_buddy
						print("Student", student)
						if student.session_status.current_active_match_type == SCH_TYPE:
							if joining:
								if student.session_status.logged_in:
									volunteer.session_status.needs_session_match = False
									student.session_status.needs_session_match = False
									student.session_status.save()
								else:
									volunteer.session_status.needs_session_match = True
							else:
								if student.session_status.logged_in:
									volunteer.session_status.needs_session_match = False
									student.session_status.needs_session_match = True
									student.session_status.save()
								else:
									volunteer.session_status.needs_session_match = False

							print("Student active is Scheduled")
							if student.session_status.logged_in:
								if volunteer.session_status.needs_new_buddy:
									volunteer.session_status.needs_session_match = True
								else:
									volunteer.session_status.needs_session_match = False
							else:
								volunteer.session_status.needs_session_match = True

						else:
							print("Student Active Type is Not Scheduled")
							if joining:
								volunteer.session_status.needs_session_match = True
							else:
								volunteer.session_status.needs_session_match = False

					volunteer.session_status.save()

					match_status = Match_Status.objects.get(session__date=localtime_now_date(),
															sch_match = volunteer.session_status.scheduled_match)
					student_redirect = process_status_scheduled(match_status, volunteer, joining)
				
	except Exception as e:
		print("Volunteer PROCESSING Exception", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="volunteer_processing_scheduled",
						location_in_function="try block volunteer_processing_scheduled",
						occurred_for_user=volunteer_ini.username,
						error_text=str(e))

	return student_redirect

def volunteer_processing_none(volunteer_ini, room, joining):
	reading_session_today = check_for_sessions_today()

	volunteer = CustomUser.objects.get(id = volunteer_ini.id)
	student_redirect = None
	try:
		if reading_session_today:
			print("\n\nVolunteer Session Status Joining", volunteer, room, volunteer.session_status.current_active_match_type)
			if joining:
				volunteer.session_status.needs_session_match = True
			else:
				volunteer.session_status.needs_session_match = False

		volunteer.session_status.save()
	except Exception as e:
		print("Volunteer PROCESSING Exception No match type", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="volunteer_processing_none",
						location_in_function="try block volunteer_processing_none",
						occurred_for_user=volunteer_ini.username,
						error_text=str(e))

	return student_redirect


@database_sync_to_async
def delete_redirects_to_user(user):
	try:
		print("Deleting redirects to user")
		redirects_to_current_user = Redirect.objects.filter(to_user = user)
		print("redirects_to_current_user", redirects_to_current_user)
		for redirect in redirects_to_current_user:
			redirect.delete()

		redirects_to_current_user = Redirect.objects.filter(to_user = user)
		print("redirects_to_current_user", redirects_to_current_user)
	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="delete_redirects_to_user",
						location_in_function="try block delete_redirects_to_user",
						occurred_for_user=user.username,
						error_text=str(e))

def staff_processing(user, room, joining):
	redirect = None
	print("STAFF PROCESSING", user, room, joining)

	return redirect

def process_user_with_manual_redirect(user, room, joining):
	redirect = None

	print("IN FUNCTION PROCESSING with manual redirect")
	return redirect	


def reset_manual_redirect(user_ini):
	user = CustomUser.objects.get(id=user_ini.id)
	session_status = User_Session_Status.objects.get(user=user)
	session_status.manual_redirect_on = False
	session_status.save()
	print("The final", user, session_status.manual_redirect_on)
	return session_status.manual_redirect_on



@database_sync_to_async
def adjust_user_session_status(user_ini, role, room_id, joining):
	sch_type = Match_Type.objects.get(name="Scheduled")
	temp_type = Match_Type.objects.get(name="Temporary")
	breakout_room_type = Room_Type.objects.get(name="Breakout")
	user = CustomUser.objects.get(id=user_ini.id)
	redirect = None
	try:
		room = Room.objects.get(id=room_id)
		if joining:
			# if room != user.session_status.room:
			user.session_status.logged_in = True			
			user.session_status.room = room	
			user.session_status.save()

			room.add_participant(user)

			try:
				print("Create User LOG")
				user_log = User_Log.objects.create(
								user = user,
								date = localtime_now_date(),
								room = room,
								time_in = localtime_now(),
								logged_in = True)
				print(user_log)
			except Exception as e:
				print("EXCEPTION Create User LOG", e)

				Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="adjust_user_session_status user log",
						location_in_function="EXCEPTION Create User LOG",
						occurred_for_user=user.username,
						error_text=str(e))


			try:
				print("*********JOINING USER SESSION TYPE ACTIVE", user.session_status.current_active_match_type)
				if role == "Volunteer":														
					if room.room_type == breakout_room_type:			

						if user.session_status.current_active_match_type == sch_type:
							print("***********Scheduled************", room, user)
							redirect = volunteer_processing_scheduled(user, room, joining)
						elif user.session_status.current_active_match_type == temp_type:
							print("^^^^^^^^^^^^^^^STOP^^^^^^^^^^^^^^^^^", room, user)
							redirect = volunteer_processing_temporary(user, room, joining)
						else:
							redirect = volunteer_processing_none(user, room, joining)

				elif role == "Student":
					if room.name == "Orientation":
						redirect = None
					else:						
						if user.session_status.current_active_match_type == sch_type:
							print("***********Scheduled************", room, user)
							redirect = student_processing_scheduled(user, room, joining)
						elif user.session_status.current_active_match_type == temp_type:
							print("^^^^^^^^^^^^^^^STOP^^^^^^^^^^^^^^^^^", room, user)
							redirect = student_processing_temporary(user, room, joining)

				else:
					print("Not Student or Volunteer")
					redirect = staff_processing(user, room, joining)


				# print("\n\n\n\nAFTER ALL PROCESSING",user, user.session_status.needs_session_match)

				# user.session_status.manual_redirect_on = False
				# user.session_status.save()
				final_r = reset_manual_redirect(user)

				print("THEN AFTER SAVE ALL PROCESSING", user, final_r)

			except Exception as e:
				Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="adjust_user_session_status active",
						location_in_function="JOINING USER SESSION TYPE ACTIVE ",
						occurred_for_user=user.username,
						error_text=str(e))

		else:
			room.remove_participant(user)
			session_status = User_Session_Status.objects.get(user=user)
			session_status.room = None
			session_status.logged_in = False
			session_status.save()

			print("*********LEAVING USER SESSION TYPE ACTIVE", user.session_status.current_active_match_type)
			if role == "Volunteer":				
				if user.session_status.current_active_match_type == sch_type:
					print("***********Volunteer Scheduled************", room, user)
					redirect = volunteer_processing_scheduled(user, room, joining)
				elif user.session_status.current_active_match_type == temp_type:
					print("^^^^^^^^^^^^^^^Volunteer STOP^^^^^^^^^^^^^^^^^", room, user)
					redirect = volunteer_processing_temporary(user, room, joining)

			elif role == "Student":
				if room.name == "Orientation":
						redirect = None
				else:
				
					if user.session_status.current_active_match_type == sch_type:
						print("***********Student Scheduled************", room, user)
						redirect = student_processing_scheduled(user, room, joining)
					elif user.session_status.current_active_match_type == temp_type:
						print("^^^^^^^^^^^^^^^Student STOP^^^^^^^^^^^^^^^^^", room, user)
						redirect = student_processing_temporary(user, room, joining)


			

			session_status = User_Session_Status.objects.get(user=user)
			session_status.room = None
			session_status.logged_in = False
			session_status.needs_session_match = False
			session_status.save()
			

			print("******LEAVING HERE", user, session_status.needs_session_match)

			if User_Log.objects.filter(user = user, logged_in = True).exists():
				try:
					user_logs = User_Log.objects.filter(
										user = user,
										logged_in = True)
					if user_logs.count() == 1:
						user_log = user_logs.first()
						user_log.time_out = localtime_now()
						user_log.logged_in = False
						user_log.save()

					else:
						last_log_id = User_Log.objects.filter(user=user).last().id

						logs = User_Log.objects.filter(user=user).exclude(id=last_log_id)
						for log in logs:
							log.logged_in = False
							log.save()

						user_log = User_Log.objects.get(
											user = user,
											logged_in = True)
						user_log.time_out = localtime_now()
						user_log.logged_in = False
						user_log.save()


				except Exception as e:
					print("\n\n\nBROKEN EXCEPTION USER LOG", e)

					Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
							function_name="adjust_user_session_status user log",
							location_in_function="try block USER LOG",
							occurred_for_user=user.username,
							error_text=e)

			else:
				try:
					last_log = User_Log.objects.filter(user = user).last()
					last_log.time_out = localtime_now()
					last_log.save()
					# user_log = User_Log.objects.create(
					# 			user = user,
					# 			date = timezone.now().date(),
					# 			room = room,
					# 			time_out = timezone.now(),
					# 			logged_in = False)
				except Exception as e:				
					Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
							function_name="adjust_user_session_status user log",
							location_in_function="no users logs true, so add to last failed",
							occurred_for_user=user.username,
							error_text=str(e))

			

			try:
				all_user_redirects = Redirect.objects.filter(user_to_redirect = user)
				for item in all_user_redirects:
					item.delete()

			except Exception as e:
				print("adjust_user_session_status ", e)
				Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="adjust_user_session_status",
						location_in_function="deleting redirects",
						occurred_for_user=user.username,
						error_text=str(e))

			



	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="adjust_user_session_status",
						location_in_function="try block adjust_user_session_status",
						occurred_for_user=user.username,
						error_text=e)
		print("\n\n\nBROKEN adjust_user_session_status", e)

	return room, redirect

@database_sync_to_async
def get_all_redirects(user_id):
	payload = ""
	try:
		payload = {}
		user = CustomUser.objects.get(id=user_id)
		try:
			all_redirects = Redirect.objects.filter(auto_send=False)
			redirect_count = all_redirects.count()
			s = LazyRedirectEncoder()
			payload['all_redirects'] = s.serialize(all_redirects)
			payload['redirect_count'] = redirect_count

			data = json.dumps(payload)
		except Exception as e:
			print("Serialize Failed", e)

	except Exception as e:
		print("\n\n\nBROKEN get_all_redirects", e)	
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="get_all_redirects",
						location_in_function="try block for get_all_redirects",
						occurred_for_user=user.username,
						error_text=e)	

	return data, redirect_count


@database_sync_to_async
def delete_redirect_by_id(user_id, redirect_id):
	payload = ""
	try:
		payload = {}
		user = CustomUser.objects.get(id=user_id)
		try:
			if Redirect.objects.filter(id=redirect_id).exists():
				print("Redirect Exists, user_id,")
				redirect = Redirect.objects.get(id=redirect_id);
				redirect.delete()
		except Exception as e:
			print("Delete Failed", e)
			Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="delete_redirect_by_id",
						location_in_function="try block for delete_redirect_by_id",
						occurred_for_user=user.username,
						error_text=str(e))


		try:
			all_redirects = Redirect.objects.filter(auto_send=False)
			redirect_count = all_redirects.count()
			s = LazyRedirectEncoder()
			payload['all_redirects'] = s.serialize(all_redirects)
			payload['redirect_count'] = redirect_count

			data = json.dumps(payload)
		except Exception as e:
			print("Serialize Failed", e)
			Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="delete_redirect_by_id",
						location_in_function="try block for Serialize Failed",
						occurred_for_user=user.username,
						error_text=(e))

		

		

	except Exception as e:
		print("\n\n\nBROKEN delete_redirect_by_id", e)	
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="delete_redirect_by_id",
						location_in_function="try block for delete_redirect_by_id outer",
						occurred_for_user=user.username,
						error_text=e)	

	return data, redirect_count

@database_sync_to_async
def get_redirect_by_id(user_id, redirect_id):
	print("\n\n\n*******get_redirect_by_id , user_id, redirect_id", user_id, redirect_id)
	try:
		if Redirect.objects.filter(id=redirect_id).exists():
			print("Redirect Exists, user_id,")
			user = CustomUser.objects.get(id=user_id)
			redirect = Redirect.objects.get(id=redirect_id);
			payload = {}
			payload['redirect_id'] = redirect.id
			payload['user_to_redirect_id'] = redirect.user_to_redirect.id
			payload['user_to_redirect_name'] = redirect.user_to_redirect.full_name
			payload['to_room_id'] = redirect.to_room.id
			payload['to_room_name'] = redirect.to_room.name
			payload['to_room_slug'] = redirect.to_room.slug
			payload['redirect_url'] = redirect.redirect_url

		# data = json.dumps(payload)

	except Exception as e:
		print("\n\n\nBROKEN get_redirect_by_id", e)	
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="get_redirect_by_id",
						location_in_function="try block for getting a redirect",
						occurred_for_user=user.username,
						error_text=e)	

	return payload

@database_sync_to_async
def get_help_requests(user):
	try:
		all_helps = Help_Request.objects.filter(done=False)
		count= all_helps.count()
		payload = {}

		s = LazyHelpEncoder()
		payload['help_requests'] = s.serialize(all_helps)
		data = json.dumps(payload)

	except Exception as e:
		print("\n\n\n\n\n BROKEN IN get_help_requests", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="get_help_requests",
						location_in_function="try block for getting help requests",
						occurred_for_user=user.username,
						error_text=e)

	return data, count


@database_sync_to_async
def mark_help_request_done(user, request_id):
	try:
		request = Help_Request.objects.get(id=request_id)
		request.mark_as_done(user.id)

	except Exception as e:
		print("BROKEN mark_help_request_done", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="mark_help_request_done",
						location_in_function="try block for mark_help_request_done",
						occurred_for_user=user.username,
						error_text=e)
	return request.done

@database_sync_to_async
def create_help_request(content):
	# new_help_requests = []
	try:
		from_user=CustomUser.objects.get(id=int(content['from_user_id']))
		from_room=Room.objects.get(id=int(content['from_room_id']))
		try:
			new_request = Help_Request.objects.create(from_user=from_user,
													from_room = from_room,
													message= content['message'],
													user_message = content['user_message'])

			all_helps = Help_Request.objects.filter(done=False)
			count= all_helps.count()

		except Exception as e:
			print("Broken", e)
			Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="create_help_request",
						location_in_function="try block for creating create_help_request",
						occurred_for_user=from_user.username,
						error_text=str(e))
		
		# new_help_requests.append(new_request)
		try:
			payload = {}
			s = LazyHelpEncoder()
			payload['help_requests'] = s.serialize(all_helps)
			data = json.dumps(payload)
		except Exception as e:
			print("BROKEN serializing help_requests", e)

			Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="create_help_request",
						location_in_function="try block for creating serializing help_requests",
						occurred_for_user=from_user.username,
						error_text=str(e))

		

	except Exception as e:
		print("BROKEN CREATE Help Request", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="create_help_request",
						location_in_function="try block for creating and serializing create_help_request",
						occurred_for_user=from_user.username,
						error_text=e)
	return data, count

@database_sync_to_async
def check_for_students(user, role, room_id):
	data=""
	count=0
	all_redirects_to_send = []
	print("\n\n\n******Checking after leaving for lonely students")
	print(user, role, room_id)


	return data, count

@database_sync_to_async
def create_manual_redirects(content):
	payload = ""
	try:
		user = CustomUser.objects.get(id=content['from_user'])
		to_send = content['users_to_send']
		to_room = Room.objects.get(id=int(content['to_room_id']))
		auto_send = True		
		all_redirects_to_send = []

		for item in to_send:
			# print(item)
			user_to_redirect = CustomUser.objects.get(id=int(item))
			user_to_redirect.session_status.manual_redirect_on = True
			user_to_redirect.session_status.save()
			redirect, created = Redirect.objects.get_or_create(user_to_redirect=user_to_redirect)
			redirect.to_room = to_room  
			redirect.auto_send = auto_send
			redirect.created_by = user  
			redirect.save()
			all_redirects_to_send.append(redirect)			

		count = len(all_redirects_to_send)
		payload = {}
		s = LazyRedirectEncoder()
		payload['manual_redirects'] = s.serialize(all_redirects_to_send)

		data = json.dumps(payload)

	except Exception as e:
		print("\n\n\nBROKEN create_manual_redirects", e)	
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="create_manual_redirects",
						location_in_function="try block for creating manual redirects",
						occurred_for_user=user.username,
						error_text=str(e))	

	return data, count



@database_sync_to_async
def to_user_unread_count(user_id):
	user = CustomUser.objects.get(id=user_id)
	try:
		user = CustomUser.objects.get(id=user_id)
		if not User_Private_Room_List.objects.filter(user=user).exists():
			pvt_list = User_Private_Room_List.objects.create(user=user)

		private_unread_count = user.private_room_list.total_unread_private
		# print(private_unread_count)
	except Exception as e:
		print("Broken", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="to_user_unread_count",
						location_in_function="try block for to_user_unread_count",
						occurred_for_user=user.username,
						error_text=str(e))	
	
	return private_unread_count


def connected_match_ws_users():
	try:
		match_group=Socket_Group.objects.get(name="match")
	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="connected_match_ws_users",
						location_in_function="try block for connected_match_ws_users",
						occurred_for_user="admin",
						error_text=str(e))	
	
	return match_group.count

def students_needing_match_count():
	try:
		needs_match=User_Session_Status.objects.filter(user__role=STUDENT_ROLE, logged_in=True,
											needs_session_match=True )
	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="students_needing_match_count",
						location_in_function="try block for students_needing_match_count",
						occurred_for_user="admin",
						error_text=str(e))
	
	return needs_match, needs_match.count()


def volunteers_needing_match_count():
	try:
		needs_match=User_Session_Status.objects.filter(user__role=VOLUNTEER_ROLE, logged_in=True,
											needs_session_match=True )
	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="volunteers_needing_match_count",
						location_in_function="try block for volunteers_needing_match_count",
						occurred_for_user="admin",
						error_text=str(e))
	
	return needs_match, needs_match.count()

def staff_logged_in_qs():
	try:
		logged_in=User_Session_Status.objects.filter(user__role=STAFF_ROLE, logged_in=True)
	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="volunteers_needing_match_count",
						location_in_function="try block for volunteers_needing_match_count",
						occurred_for_user="admin",
						error_text=str(e))
	
	return logged_in, logged_in.count()

def user_match_status(user):
	try:
		if user.role == VOLUNTEER_ROLE:
			if user.session_status.temporary_buddy:
				match_statuses = Match_Status.objects.filter(Q(session__date=localtime_now_date()),
														Q(sch_match__volunteer=user)|
														Q(temp_match__teacher_user=user)|
														Q(sch_match__student=user.session_status.temporary_buddy))

			else:
				match_statuses = Match_Status.objects.filter(Q(session__date=localtime_now_date()),
														Q(sch_match__volunteer=user)|
														Q(temp_match__teacher_user=user))
		elif user.role == STUDENT_ROLE:
			if user.session_status.temporary_buddy:
				print("Has TEMP BUDDY")
				match_statuses = Match_Status.objects.filter(Q(session__date=localtime_now_date()),
														Q(sch_match__student=user)|
														Q(temp_match__student_user=user)|
														Q(sch_match__volunteer=user.session_status.temporary_buddy))

			else:
				match_statuses = Match_Status.objects.filter(Q(session__date=localtime_now_date()),
														Q(sch_match__student=user)|
														Q(temp_match__student_user=user))

		else:
			match_statuses = Match_Status.objects.filter(Q(session__date=localtime_now_date()),
													Q(sch_match__volunteer=user)|
													Q(temp_match__teacher_user=user))

		print("MATCH STATUS FOR USER", user, match_statuses)
	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="user_match_status",
						location_in_function="try block for user_match_status",
						occurred_for_user=user.username,
						error_text=str(e))
	

	return match_statuses


@database_sync_to_async
def get_session_stats(user):
	try:
		rooms = Room.objects.all()
		payload = {}
		s = LazyRoomParticipantsEncoder()
		payload['rooms_participants'] = s.serialize(rooms)

		payload['connected_match_users'] = connected_match_ws_users()


		all_redirects = Redirect.objects.filter(auto_send=False)
		redirect_count = all_redirects.count()
		s = LazyRedirectEncoder()
		payload['all_redirects'] = s.serialize(all_redirects)
		payload['redirect_count'] = redirect_count



		s = LazySessionStatusEncoder()
		students_in_need, payload['students_needing_match_count'] = students_needing_match_count()
		payload['students_needing_match'] = s.serialize(students_in_need) 

		volunteers_in_need, payload['volunteers_needing_match_count'] = volunteers_needing_match_count()
		payload['volunteers_needing_match'] = s.serialize(volunteers_in_need) 

		staff_logged_in, payload['staff_logged_in_count'] = staff_logged_in_qs()
		payload['staff_logged_in'] = s.serialize(staff_logged_in) 

		try:
			match_statuses = user_match_status(user)
			# match_statuses = Match_Status.objects.filter(session__date=timezone.now().date())
			s=LazyMatchStatusEncoder()
			payload['match_statuses'] = s.serialize(match_statuses) 
		except Exception as e:
			print("\n\n\n\n*** Match STATUS Exception HERE", e)
			Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="get_session_stats",
						location_in_function="try block Match STATUS Exception HERE 1",
						occurred_for_user=user.username,
						error_text=str(e))
		

		if user.role.name == "Staff":
			# print("\n\n\n*****Staff Joining, These Stats Needed")
			all_helps = Help_Request.objects.filter(done=False) 
			count= all_helps.count()
			s = LazyHelpEncoder()
			payload['help_requests'] = s.serialize(all_helps)
			payload['help_request_count'] = count

			

		# else:
		# 	print('\n\n****Not Staff JOINING', user, type(user))

		data = json.dumps(payload)

	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="get_rooms_and_participants",
						location_in_function="try block for serializing rooms and participants",
						occurred_for_user=user.username,
						error_text=e)
		print("\n\n\nBROKEN get_rooms_and_participants", e)

	# print("\n\n\n\nDATA IN SESSION STATS", data)

	return data






@database_sync_to_async
def create_log_of_error(socket_info):
	try:
		Websocket_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])

	except Exception as e:
		print("\n\n\nBROKEN create_log_of_error")

@database_sync_to_async
def get_user_or_error(username):
	try:
		user = CustomUser.objects.get(username=username)
		role = user.role.name		

	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="get_user_or_error",
						location_in_function="try block for getting user and role",
						occurred_for_user=username,
						error_text=str(e))
		print("\n\n\nBROKEN get_user_or_error", e)	

	return user, role


@database_sync_to_async
def adjust_socket_group_participants(user, socket_group, in_group):
	try:
		group, created = Socket_Group.objects.get_or_create(name=socket_group)

		if in_group:
			group.add_user(user)
		else:
			group.remove_user(user)

	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="adjust_socket_group_participants",
						location_in_function="try block adjusting socket_group",
						occurred_for_user=user.username,
						error_text=str(e))
		print("\n\n\nBROKEN adjust_socket_group_participants", e)	



@database_sync_to_async
def private_get_connected_users(room):
	try:
		connected_users = room.connected_users.all()
		user1 = room.user1
		user2 = room.user2		
		# print("count", count)	
	except:
		print("\n\n\nBROKEN get_connected_users")
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="private_get_connected_users",
						location_in_function="try block private_get_connected_users",
						occurred_for_user=room.name,
						error_text=str(e))
	return connected_users, user1, user2


@database_sync_to_async
def create_private_chat_room_message(room, user, content):
	try:
		message = ""
		# print("create_room_chat_message")
		# print('room', room)
		# print('user', user)
		# print('content', content)
		to_user = CustomUser.objects.get(id=content['to_user'])

		message = RoomChatMessage.objects.create(from_user= user,
												to_user=to_user,
												user=user,
												room=room,
												content=content['pvt_message'])
	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="create_private_chat_room_message",
						location_in_function="try block create_private_chat_room_message",
						occurred_for_user=user.username,
						error_text=str(e))
	
	return message



@database_sync_to_async
def append_unread_msg_if_not_connected(sender, room, user, connected_users, message):
	try:
		if not user in connected_users: 
			try:
				unread_msgs = UnreadChatRoomMessages.objects.get(room=room, user=user)
				unread_msgs.most_recent_message = "New Message from " + sender.full_name
				unread_msgs.last_message = message
				unread_msgs.count += 1
				unread_msgs.save()
				unread_msgs.unread_msgs.add(message)
				
			except UnreadChatRoomMessages.DoesNotExist:
				UnreadChatRoomMessages(room=room, user=user,
										count=1, most_recent_message=message.content,
										last_message=message).save()
				pass

			user.private_room_list.total_all_unread()
	except Exception as e:
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="append_unread_msg_if_not_connected",
						location_in_function="try block append_unread_msg_if_not_connected",
						occurred_for_user=user.username,
						error_text=str(e))
	
	return



@database_sync_to_async
def get_private_rooms_for_user(user_id):
	data = ""
	count = ""
	try:
		user = CustomUser.objects.get(id=user_id)
		# print("***********get_private_rooms_for_user")
		if not User_Private_Room_List.objects.filter(user=user).exists():
			pvt_list = User_Private_Room_List.objects.create(user=user)
	

		list_rooms = user.private_room_list.private_rooms.all().order_by('-last_use')
		count = list_rooms.count()
		# print("list_rooms", list_rooms)
		# print("count", count)

		payload = {}
		s = LazyPrivateRoomEncoder()
		payload['private_rooms'] = s.serialize(list_rooms)
		data = json.dumps(payload)


	except Exception as e:
		print("BROKEN get_private_rooms_for_user", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="get_private_rooms_for_user",
						location_in_function="try block for get_private_rooms_for_user",
						occurred_for_user=user.username,
						error_text=str(e))
	# return unique_senders_data, message_data, count
	return data, count

@database_sync_to_async
def get_private_room_or_error(room_id, user):
	try:
		room = PrivateChatRoom.objects.get(pk=room_id)
		user1 = room.user1
		user2 = room.user2
		if user != user1 and user != user2:
			raise ClientError("ROOM_ACCESS_DENIED", "You do not have permission to join this room.")
		# else:
		# 	print("Allowed")

	except Exception as e:
		print("BROKEN get_private_room_or_error", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="get_private_room_or_error",
						location_in_function="try block for get_private_room_or_error",
						occurred_for_user=user.username,
						error_text=str(e))

	return room


@database_sync_to_async
def private_connect_user(room, user):
	# add user to connected_users list
	user = CustomUser.objects.get(pk=user.id)
	return room.connect_user(user)


@database_sync_to_async
def private_disconnect_user(room, user):
	# remove from connected_users list
	user = CustomUser.objects.get(pk=user.id)
	return room.disconnect_user(user)


@database_sync_to_async
def unread_private_msg_by_user(user_id):
	count = 0
	try:
		user = CustomUser.objects.get(id=user_id)


		if UnreadChatRoomMessages.objects.filter(user=user).exists():
			pvt_list = UnreadChatRoomMessages.objects.filter(user=user)

			for room in pvt_list:
				count = count + room.count
		# print(private_unread_count)
	except Exception as e:
		print("Broken unread_private_msg_by_user", e)
		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
						function_name="unread_private_msg_by_user",
						location_in_function="try block for unread_private_msg_by_user",
						occurred_for_user=str(user_id),
						error_text=str(e))
	
	return count


# @database_sync_to_async
# def get_rooms_and_participants(user):
# 	try:
# 		rooms = Room.objects.all()
# 		payload = {}
# 		s = LazyRoomParticipantsEncoder()
# 		payload['rooms_participants'] = s.serialize(rooms)

# 		data = json.dumps(payload)

# 	except Exception as e:
# 		Websocket_Error.objects.create(file="database_sync_to_async_functions.py",
# 						function_name="get_rooms_and_participants",
# 						location_in_function="try block for serializing rooms and participants",
# 						occurred_for_user=user.username,
# 						error_text=e)
# 		print("\n\n\nBROKEN get_rooms_and_participants", e)

# 	return data
