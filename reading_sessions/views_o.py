from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
from urllib.parse import urlencode
from itertools import chain
import datetime
import calendar

import json
from json import dumps
from django.http import JsonResponse, HttpResponse
from django.core import serializers

from users import jwt_token

from reading_sessions.models import *
from site_admin.models import *
from websockets.models import *
from users.models import *
from jitsi_data.models import *

from websockets.serializers import *
from jitsi_data.serializers import *

from reading_sessions.forms import End_Session_Evaluation_Form, Link_End_Session_Evaluation_Form



# Create your views here.

DEBUG = False
WEB = True


def all_user_landing_pages(user, context):
	# print("\n\n\n\n******View USER", user)
	# print("View This needs to happen for all users on the landing page")
	date_time_now = timezone.localtime(timezone.now())
	user_status, created = User_Status.objects.get_or_create(user=user)
	# print("User Status", user_status, user_status.has_status_redirect)
	if Status_Redirect.objects.filter(user_to_redirect=user).exists():
		status_redirect = Status_Redirect.objects.get(user_to_redirect=user)
		status_redirect.delete()
		user_status.has_status_redirect = False
		user_status.save()
	else:
		user_status.has_status_redirect = False
		user_status.save()


	if Day_With_Team_Meeting.objects.filter(date=date_time_now).exists():
		day_with_team_meeting = Day_With_Team_Meeting.objects.get(date=date_time_now)
		context['day_with_team_meeting'] = day_with_team_meeting

	if Day_With_Orientation_Meeting.objects.filter(date=date_time_now).exists():
		context['orientation_today'] = True
		day_with_o_meeting = Day_With_Orientation_Meeting.objects.get(date=date_time_now)
		context['day_with_o_meeting'] = day_with_o_meeting	
		if user in day_with_o_meeting.allowed_participants.all():
			if date_time_now.time() >= day_with_o_meeting.time_start and date_time_now.time() <= day_with_o_meeting.time_end:
				context['show_orientation_button'] = True
			else:
				context['show_orientation_button'] = False
		else:
			context['show_orientation_button'] = False

	else:
		context['day_with_o_meeting'] = None
		context['show_orientation_button'] = False
		context['orientation_today'] = False

	context['orientation_complete'] = user.session_status.orientation_complete
	o_room = Room.objects.get(name="Orientation")
	context['orientation_room'] = o_room

	troubleshooting_room = Room.objects.get(name="Connection Testing")
	context['troubleshooting_room'] = troubleshooting_room	
	

	# user_in_rooms = user.room_participants.all()
	# # print("all_user_landing_pages", user_in_rooms)
	# for old_room in user_in_rooms:		
	# 	# print("In ROOM", old_room, old_room.num_participants, old_room.participants.all())
	# 	old_room.remove_participant(user)
	# 	# print("After ROOM", old_room, old_room.num_participants, old_room.participants)


	user.session_status.on_landing_page = True	
	user.session_status.manual_redirect_on = False			
	user.session_status.save()
		
	return context

def active_semester():
	semester = Semester.objects.get(active_semester=True)
	return semester

def todays_jitsi_chat():
	todays_jitsi_chat = Jitsi_Chat_Room.objects.filter(date_created=timezone.localtime(timezone.now())).first()

	if not todays_jitsi_chat:
		now = timezone.localtime(timezone.now())
		title = "Jitsi Chat - " + now.date().strftime("%B %d, %Y")
		todays_jitsi_chat = Jitsi_Chat_Room.objects.create(title=title)

	return todays_jitsi_chat

def todays_staff_chat():
	todays_staff_chat = Staff_Chat_Room.objects.filter(date_created=timezone.localtime(timezone.now())).first()

	if not todays_staff_chat:
		now = timezone.localtime(timezone.now())
		title = "Staff Chat - " + now.date().strftime("%B %d, %Y")
		todays_staff_chat = Staff_Chat_Room.objects.create(title=title)
		staff = CustomUser.objects.filter(role__name = "Staff")
		for member in staff:
			member.unread_staff.unread_count = 0 
			member.unread_staff.save()

	return todays_staff_chat



	# todays_staff_chat = Staff_Chat_Room.objects.filter(date_created=timezone.now().date()).first()
	# print("this", todays_staff_chat, todays_staff_chat.id)

	# if not todays_staff_chat:
	# 	print("IN the not")
	# 	title = "Staff Chat - " + timezone.now().date().strftime("%B %d, %Y")
	# 	todays_staff_chat = Staff_Chat_Room.objects.create(title=title)
	# 	staff = CustomUser.objects.filter(role__name = "Staff")
	# 	for member in staff:
	# 		member.unread_staff.unread_count = 0 
	# 		member.unread_staff.save()
	# print("THE ID IS ", todays_staff_chat.id)
	# return todays_staff_chat

def all_users():
	users = CustomUser.objects.all().order_by('first_name')
	return users

def all_staff():
	users = CustomUser.objects.filter(role__name="Staff").order_by('first_name')
	return users

def all_students():
	users = CustomUser.objects.filter(role__name="Student").order_by('first_name')
	return users

def all_volunteers():
	users = CustomUser.objects.filter(role__name="Volunteer").order_by('first_name')
	return users

def all_students_progresses():
	users = Student_Progress.objects.filter(user__user_dropped=False).order_by('initial_assessment','user__username')
	return users


def sessions_today():
	today = timezone.now()
	todays_sessions = Daily_Session.objects.filter(date=today)
	return todays_sessions


def room_additional_context(context,user):
	user_status, created = User_Status.objects.get_or_create(user=user)
	# print("User Status", user_status, user_status.has_status_redirect)
	if Status_Redirect.objects.filter(user_to_redirect=user).exists():
		status_redirect = Status_Redirect.objects.get(user_to_redirect=user)
		status_redirect.delete()
		user_status.has_status_redirect = False
		user_status.save()
	else:
		user_status.has_status_redirect = False
		user_status.save()

	context['active_semester'] = active_semester()

	user_role = user.role.name
	context['user_role'] = user_role

	members = CustomUser.objects.all().order_by('username')
	context['members'] = members

	todays_jitsi_chat_room = todays_jitsi_chat()
	context['todays_jitsi_chat_room'] = todays_jitsi_chat_room

	rooms = Room.objects.all().order_by('id')
	context['rooms'] = rooms

	today_date = timezone.now().date()
	today = today_date.weekday()
	today_day_of_week = calendar.day_name[today]
	print("\n\n\n\n\n\ntoday_day_of_week", today_day_of_week)

	context['today_date'] = today_date
	context['today'] = today_day_of_week

	server_time = Server_Time.objects.get(active=True)
	context['server_time'] = server_time
	context['server_time_entry_start'] = str(server_time.entry_allowed_start)
	context['server_time_entry_end'] = str(server_time.entry_allowed_end)
	time_now = timezone.localtime(timezone.now()).time()
	print(time_now)
	print("server_time", server_time.days.all())

	this_day = Day.objects.get(name=today_day_of_week)
	print("This day", this_day) 

	if time_now >= server_time.start_time and time_now <= server_time.end_time:
		print("In the time window")
		
		
		if this_day in server_time.days.all():
			print("yes in days")
			context['load_jitsi_script'] = True
		else:
			print("no in days")
			context['load_jitsi_script'] = False
	else:
		print("server off")
		context['load_jitsi_script'] = False



	print("context['load_jitsi_script']", context['load_jitsi_script'])

	if WEB:
		context['debug_mode'] = DEBUG
		context['debug'] = settings.DEBUG
	else:
		context['debug_mode'] = settings.DEBUG
		context['debug'] = DEBUG

	if user_role == "Staff":
		if Day_With_Daily_Session.objects.filter(date=timezone.now()).exists():
			day_with_session = Day_With_Daily_Session.objects.get(date=timezone.now())
			context['day_with_session'] = day_with_session		

		todays_staff_chat_room = todays_staff_chat()
		context['todays_staff_chat_room'] = todays_staff_chat_room

		context['all_students'] = all_students()
		context['all_volunteers'] = all_volunteers()
		context['all_staff'] = all_staff()
		context['current_students'] = all_students_progresses()
		without_assessments = Student_Progress.objects.filter(user__user_dropped=False, initial_assessment=False).count()
		context['without_assessment'] = without_assessments

		context['temp_match_type'] = Temporary_Match_Type.objects.get(short_name='I-S')

		j_rooms = Jitsi_Meeting_Room.objects.all().order_by('-count', 'student_alone', 'mismatch', 'room')
		context['j_rooms'] = j_rooms

	elif user_role == "Student":
		pass

	elif user_role == "Volunteer":
		student_profiles = Student_Profile.objects.all().order_by('user__username')
		context['student_profiles'] = student_profiles


	

	return context


def additional_context_all(context, user):
	print("\n\n\n\n\n\nADDITIONAL", user)
	#Staff & Non-Staff
	# context['active_semester'] = active_semester()

	days = Day.objects.all().order_by('id')
	context['days'] = days

	slots = active_semester().day_time_slots.all()
	context['slots'] = slots

	user_role = user.role.name
	context['user_role'] = user_role

	today_date = timezone.now().date()
	today = today_date.weekday()
	today_day_of_week = calendar.day_name[today]
	print("\n\n\n\n\n\ntoday_day_of_week", today_day_of_week)

	context['today_date'] = today_date
	context['today'] = today_day_of_week

	server_time = Server_Time.objects.get(active=True)
	context['server_time'] = server_time
	context['server_time_entry_start'] = str(server_time.entry_allowed_start)
	context['server_time_entry_end'] = str(server_time.entry_allowed_end)
	time_now = timezone.localtime(timezone.now()).time()
	print(time_now)
	print("server_time", server_time.days.all())

	this_day = Day.objects.get(name=today_day_of_week)
	print("This day", this_day) 

	if time_now >= server_time.start_time and time_now <= server_time.end_time:
		print("In the time window")
		
		
		if this_day in server_time.days.all():
			print("yes in days")
			context['load_jitsi_script'] = True
		else:
			print("no in days")
			context['load_jitsi_script'] = False
	else:
		print("server off")
		context['load_jitsi_script'] = False

	# print("\n\n\n\n\ncontext['load_jitsi_script']", context['load_jitsi_script'])


	user_token = user.new_meeting_token()
	context['token'] = user_token

	return context

def get_token(user):
	user_token = user.new_meeting_token()
	# user_token = user.meeting_token()
	# print("Token", user, user_token)
	return user_token

def meeting_room_view(request, room_slug):
	# print("\n\n\n\n\n\n VIEW ROOM SLUG", room_slug, request.user)
	context = {}	
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		room = Room.objects.get(slug=room_slug)
		context['page_title'] = room.name
		context['room'] = room

		if user.is_approved:
			user_in_rooms = user.room_participants.all()
			# print("APPROVED", user_in_rooms)
			for old_room in user_in_rooms:
				
				# print("In ROOM", old_room, old_room.num_participants, old_room.participants.all())
				old_room.remove_participant(user)
				# print("After ROOM", old_room, old_room.num_participants, old_room.participants)


			user.session_status.room = room
			user.session_status.on_landing_page = False
			user.session_status.save()

			room.add_participant(user)


			context=room_additional_context(context, user)

			
			context['token'] = get_token(user)

			# server_time = Server_Time.objects.get(active=True)
			# context['server_time'] =server_time
			# context['entry_check'] = entry_check()

			if user.role.name == "Staff":
				pass
			elif user.role.name == "Student":
				pass
			elif user.role.name == "Volunteer":
				pass

			else:
				print("Else Role")

			print("Rendering ROOM")

			return render(request, "reading_sessions/room.html", context)
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def initial_entry_view(request):
	context = {}
	context['page_title'] = "Initial Entry"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		user_status, created = User_Status.objects.get_or_create(user=user)
		# print("User Status", user_status, user_status.has_status_redirect)
		if Status_Redirect.objects.filter(user_to_redirect=user).exists():
			status_redirect = Status_Redirect.objects.get(user_to_redirect=user)
			status_redirect.delete()
			user_status.has_status_redirect = False
			user_status.save()
		else:
			user_status.has_status_redirect = False
			user_status.save()
		if user.is_approved:
			user_in_rooms = user.room_participants.all()
			# print("initial_entry_view", user_in_rooms)
			for old_room in user_in_rooms:		
				# print("In ROOM", old_room, old_room.num_participants, old_room.participants.all())
				old_room.remove_participant(user)
				# print("After ROOM", old_room, old_room.num_participants, old_room.participants)


			user.session_status.on_landing_page = False
			

			if user.role.name == "Student":
				match_pending_room = Room.objects.get(room_type__letter="P")
				# print("View Match Pending Room",match_pending_room)
				if user.session_status.current_active_match_type.name == "Scheduled":
					# print("\n\n\n\n\nScheduled")
					if user.session_status.needs_new_buddy:
						return redirect('reading_sessions:room', room_slug=match_pending_room.slug)
					else:
						if user.session_status.scheduled_match:
							volunteer = user.session_status.scheduled_match.volunteer
							if volunteer.session_status.logged_in:
								return redirect('reading_sessions:room',
												 room_slug=volunteer.session_status.room.slug)
							else:
								return redirect('reading_sessions:room', room_slug=match_pending_room.slug)
						else:
							return redirect('reading_sessions:room', room_slug=match_pending_room.slug)

				elif user.session_status.current_active_match_type.name == "Temporary":
					if user.session_status.temp_match:
						buddy = user.session_status.temp_match.teacher_user
						if buddy.session_status.logged_in:
							return redirect('reading_sessions:room',
											 room_slug=buddy.session_status.room.slug)
						else:
							return redirect('reading_sessions:room', room_slug=match_pending_room.slug)
					else:
						return redirect('reading_sessions:room', room_slug=match_pending_room.slug)
				else:
					return redirect('reading_sessions:room', room_slug=match_pending_room.slug)

			elif user.role.name == "Volunteer":
				room = Room.unoccupied_breakout_first()
				room.add_participant(user)
				user.session_status.room = room
				user.session_status.save()
				return redirect('reading_sessions:room', room_slug=room.slug)

			elif user.role.name == "Staff":
				lobby = Room.objects.get(name="Session Lobby")
				return redirect('reading_sessions:room', room_slug=lobby.slug)
								

			

			return render(request, "reading_sessions/initial_entry.html", context)
			# else:
			# 	return redirect('home')
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')


def student_landing_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Student Home"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:

			
			if user.role.name == "Student":
				# user.session_status.on_landing_page = True
				# user.session_status.save()
				context=all_user_landing_pages(user, context)
				context=additional_context_all(context, user)
				# server_time = Server_Time.objects.get(active=True)
				# context['server_time'] = server_time
				# context['entry_check'] = entry_check()

				scheduled_slots = user.student_profile.scheduled_day_time_slots.all()
				context['scheduled_slots'] = scheduled_slots


				todays_sessions = sessions_today()

				session_for_today = None
				show_join_button = False
				next_scheduled_session = None
				student_contact = Secondary_Role.objects.get(name="Student Contact")
				student_contacts = student_contact.roles.all()
				context['student_contacts'] = student_contacts
				# student_contacts = CustomUser.objects.filter(Q(secondary_roles__in=student_contact))
				# student_contacts = CustomUser.objects.filter(secondary_roles__in=student_contact)
				# print("Student CONTACT", student_contacts)

				if user.session_status.current_active_match_type: 
					if user.session_status.current_active_match_type.name == "Scheduled":
						print("\n\n\n\nVIEW Current Type is Scheduled")

					if user.session_status.scheduled_match:
						for session in todays_sessions:
							if session in user.session_status.scheduled_match.sessions_scheduled.all():
								session_for_today = session

						if session_for_today:
							entry_allowed_start_time = timezone.localtime(session_for_today.student_entry_allowed_start)
							context['entry_allowed'] = entry_allowed_start_time.time()


							entry_allowed_end_time = timezone.localtime(session_for_today.student_entry_allowed_end)
							context['entry_end'] = entry_allowed_end_time.time()

							# print("Time now", timezone.now())
							# print("Local Time now", timezone.localtime(timezone.now()))
							# print("start", session_for_today.student_entry_allowed_start)
							# print("end",  session_for_today.student_entry_allowed_end)
							start_local = timezone.localtime(session_for_today.student_entry_allowed_start)
							end_local = timezone.localtime(session_for_today.student_entry_allowed_end)
							# print("local start", start_local)
							# print("local end",  end_local)

							if  timezone.localtime(timezone.now()) >= start_local and \
							 timezone.localtime(timezone.now()) < end_local:
								show_join_button = True	
							else:
								show_join_button = False
								if  timezone.localtime(timezone.now()) >= end_local:
									context['message_for_user'] = System_Message.objects.get(name="Session Ended")
									context['next_session_message'] = System_Message.objects.get(name="Next Session")
									next_scheduled_session = user.session_status.scheduled_match.sessions_scheduled.filter(
																		session_start_date_time__gte=timezone.now()).first()
								else:
									if  timezone.localtime(timezone.now()) <= start_local:
										context['message_for_user'] = System_Message.objects.get(name="Too Early")
									
						else:
							context['next_session_message'] = System_Message.objects.get(name="Next Session")
							next_scheduled_session = user.session_status.scheduled_match.sessions_scheduled.filter(
																		date__gte=timezone.now()).first()


								

						
					# else:
					# 	print("Current Type is NOT scheduled")
					# 	for session in todays_sessions:
					# 		if session in user.session_status.scheduled_match.sessions_scheduled.all():
					# 			session_for_today = session


				# print("\n\n\n\n View Final Student Stats")
				# print("View session_for_today", session_for_today)
				# print("View show_join_button", show_join_button)
				# print("View next_scheduled_session", next_scheduled_session)

				context['session_for_today'] = session_for_today
				context['show_join_button'] = show_join_button
				context['next_scheduled_session'] = next_scheduled_session

				

				return render(request, "reading_sessions/student_landing.html", context)
			else:
				return redirect('home')
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')


def volunteer_landing_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Volunteer Home"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:

			
			
			if user.role.name == "Volunteer":
				# user.session_status.on_landing_page = True				
				# user.session_status.save()
				context=all_user_landing_pages(user, context)
				context=additional_context_all(context, user)
				todays_sessions = sessions_today()
				first_session = todays_sessions.first()
				last_session = todays_sessions.last()

				additional_roles = user.secondary_roles.all()
				context['additional_roles'] = additional_roles
				# print("\n\n\n\nadditional_roles", additional_roles)
				mega_teams = Mega_Team.objects.all()
				context['mega_teams'] = mega_teams
				# print("mega_teams", mega_teams)

				coordinator = Secondary_Role.objects.get(name="Coordinator")
				if coordinator in additional_roles:
					is_coordinator = True
					coor_mega_team = Mega_Team.objects.get(coordinator=user)
					context['coor_mega_team']=coor_mega_team
				else:
					is_coordinator = False
				context['is_coordinator'] = is_coordinator
				# print("is_coordinator", is_coordinator)


				facilitator = Secondary_Role.objects.get(name="Facilitator")
				if facilitator in additional_roles:
					is_facilitator = True					
				else:
					is_facilitator = False
				context['is_facilitator'] = is_facilitator
				# print("is_facilitator", is_facilitator)

				team_leader = Secondary_Role.objects.get(name="Team Leader")
				if team_leader in additional_roles:
					is_team_leader = True
					tl_team = Team.objects.get(leader=user)
					context['tl_team']=tl_team					
				else:
					is_team_leader = False
				context['is_team_leader'] = is_team_leader
				# print("is_team_leader", is_team_leader)

				full_access = Secondary_Role.objects.get(name="Full Access")
				if full_access in additional_roles:
					full_access = True					
				else:
					full_access = False
				context['needs_full_access'] = full_access
				# print("full_access", full_access)

				# print("\n\n\n\nTimezone NOW", timezone.localtime(timezone.now()))
				# print("first_session.entry_allowed_start", timezone.localtime(first_session.entry_allowed_start))
				# print("last_session.entry_allowed_end", timezone.localtime(last_session.entry_allowed_end))
				scheduled_slots = user.volunteer_profile.scheduled_day_time_slots.all()
				context['scheduled_slots'] = scheduled_slots

				show_join_button = False
					
				if todays_sessions.count() > 0:
					# print("\n\n\n\n\nSessions Today")
					if timezone.localtime(timezone.now()) >= timezone.localtime(first_session.entry_allowed_start) and \
					timezone.localtime(timezone.now()) < timezone.localtime(last_session.entry_allowed_end):
						show_join_button = True
						# print("Show button True")
					else:
						show_join_button = False
						# print("Show button False")
						if timezone.localtime(timezone.now()) >= timezone.localtime(last_session.entry_allowed_end):
							context['message_for_user'] = System_Message.objects.get(name="Sessions Over")						
						else:
							if timezone.localtime(timezone.now()) <= timezone.localtime(first_session.entry_allowed_start):
								context['message_for_user'] = System_Message.objects.get(name="Sessions Not Started")


					entry_allowed_start_time = timezone.localtime(first_session.entry_allowed_start)
					context['entry_allowed'] = entry_allowed_start_time.time()

					entry_allowed_end_time = timezone.localtime(last_session.entry_allowed_end)
					context['entry_end'] = entry_allowed_end_time.time()
				else:
					context['message_for_user'] = System_Message.objects.get(name="No Reading Sessions")

					# print("\n\n\n\nView Final Volunteer Stats")
					# print("View show_join_button", show_join_button)
				

				
				context['show_join_button'] = show_join_button


				return render(request, "reading_sessions/volunteer_landing.html", context)
			else:
				return redirect('home')
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def no_link_session_evaluation_view(request, *args, **kwargs):
	# form=Link_End_Session_Evaluation_Form(request.POST or None, initial=initial_data)	
	context = {}
	context['page_title'] = "Session Evaluation"
	user = request.user

	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			user_in_rooms = user.room_participants.all()
			# print("link session_evaluation", user_in_rooms)
			for old_room in user_in_rooms:		
				# print("In ROOM", old_room, old_room.num_participants, old_room.participants.all())
				old_room.remove_participant(user)
				# print("After ROOM", old_room, old_room.num_participants, old_room.participants)

			context['role'] = user.role.name

			if user.role.name == "Staff" or user.role.name == "Volunteer":			
			
				students = CustomUser.objects.all().order_by('username')
				context['students'] = students

				reading_levels = Reading_Level.objects.all().order_by('id')
				context['reading_levels'] = reading_levels

				relational_engagement = Relational_Engagement.objects.all().order_by('id')
				context['relational_engagement'] = relational_engagement

				assessment_levels = Evaluation_Level.objects.all().order_by('id')
				context['assessment_levels'] = assessment_levels

				follow_up_types = Follow_Up_Type.objects.all().order_by('id')
				context['follow_up_types'] = follow_up_types

				arrivals = Arrival_Description.objects.all().order_by('id')
				context['arrivals'] = arrivals

				display_scheduled = False

				if user.session_status.scheduled_buddy:
					user_scheduled_buddy = user.session_status.scheduled_buddy
				else:
					user_scheduled_buddy = None

				initial_data={
					"completed_by": user,
					"scheduled_student": user_scheduled_buddy,
				}

				
				context['display_scheduled'] = display_scheduled

			
				form=Link_End_Session_Evaluation_Form(request.POST or None, initial=initial_data)	
					
				if request.POST:
					# form = End_Session_Evaluation_Form(request.POST)
					# student = request.POST.get('scheduled_student')
					# temp_student = request.POST.get('temp_student')
					# print("STUDENT IN VIEW", student)
					# print("TEMP STUDENT IN VIEW", temp_student)

					# form['scheduled_student']=scheduled_buddy

					if form.is_valid():	
						print("Form is Valid")						
						form.save()

						messages.success(request, 'Session Evaluation Successfully Submitted')
						return redirect("reading_sessions:volunteer_home")
					else:
						print(form.errors)
						form = Link_End_Session_Evaluation_Form(request.POST)
						# errors = form.errors
						# print("CONTEXT",context)
						# for item in context:
						# 	print(item)  
						# initial_data={
						# 	"completed_by": user,
						# 	"scheduled_student": user_scheduled_buddy,
						# 	"read_with_scheduled": request.POST.get('read_with_scheduled')
						# }         
						
				context['form'] = form


				return render(request, "reading_sessions/late_session_evaluation.html", context)
			else:
				return redirect('home')
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def link_session_evaluation_view(request, *args, **kwargs):
	print("\n\n\n\nlink_session_evaluation_view")
	context = {}
	context['page_title'] = "Session Evaluation"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			user_in_rooms = user.room_participants.all()
			# print("session_evaluation", user_in_rooms)
			for old_room in user_in_rooms:		
				# print("In ROOM", old_room, old_room.num_participants, old_room.participants.all())
				old_room.remove_participant(user)
				# print("After ROOM", old_room, old_room.num_participants, old_room.participants)

			context['role'] = user.role.name
			if user.role.name == "Staff" or user.role.name == "Volunteer":
			
			
				students = CustomUser.objects.all().order_by('username')
				context['students'] = students

				reading_levels = Reading_Level.objects.all().order_by('id')
				context['reading_levels'] = reading_levels

				relational_engagement = Relational_Engagement.objects.all().order_by('id')
				context['relational_engagement'] = relational_engagement

				assessment_levels = Evaluation_Level.objects.all().order_by('id')
				context['assessment_levels'] = assessment_levels

				follow_up_types = Follow_Up_Type.objects.all().order_by('id')
				context['follow_up_types'] = follow_up_types

				arrivals = Arrival_Description.objects.all().order_by('id')
				context['arrivals'] = arrivals

			

				if user.role.name == "Volunteer":
					if user.volunteer_profile.match_needed:
						display_scheduled = False
						context['display_scheduled'] = display_scheduled
						context['match_needed'] = user.volunteer_profile.match_needed

					else:
						context['match_needed'] = user.volunteer_profile.match_needed
						if user.session_status.scheduled_buddy:
							display_scheduled = True
							scheduled_buddy = user.session_status.scheduled_buddy
							context['scheduled_buddy'] = scheduled_buddy
							context['display_scheduled'] = display_scheduled

						else:
							display_scheduled = False
							context['display_scheduled'] = display_scheduled

				elif user.role.name == "Staff":
					display_scheduled = False
					context['display_scheduled'] = display_scheduled
					context['match_needed'] = True

				if request.POST:
					form = End_Session_Evaluation_Form(request.POST)
					student = request.POST.get('scheduled_student')
					temp_student = request.POST.get('temp_student')
					# print("STUDENT IN VIEW", student)
					# print("TEMP STUDENT IN VIEW", temp_student)

					# form['scheduled_student']=scheduled_buddy

					if form.is_valid():							
						form.save()

						messages.success(request, 'Session Evaluation Successfully Submitted')
						return redirect("reading_sessions:volunteer_home")
					else:
						if form.errors:
							for field in form:
								for error in field.errors:
									print("Error ", field.name, error)
									if field.name == "read_with_scheduled":
										context['read_with_scheduled_error'] = error

									if field.name == "scheduled_student_attendance":
										context['scheduled_student_attendance_error'] = error

									if field.name == "temp_student":
										context['temp_student_error'] = error


						# print(form.errors)
						# errors = form.errors
						form= End_Session_Evaluation_Form(
							initial = {
								"date": timezone.localtime(timezone.now()).date(),
								"completed_by": user,
								"scheduled_student": scheduled_buddy,
								"read_with_scheduled": request.POST.get('read_with_scheduled'),
								# "volunteer": match.volunteer,
								# "scheduled_slots": match.scheduled_slots.all(),	
								# "match_active": match.match_active,											
							}
						)
						context['form'] = form

						# print("CONTEXT",context)
						# for item in context:
						# 	print(item)
			           
						

				else:
					if display_scheduled:
					
						form= End_Session_Evaluation_Form(
								initial = {
									"date": timezone.localtime(timezone.now()).date(),
									"completed_by": user,
									"scheduled_student": scheduled_buddy,
									# "read_with_scheduled": request.POST.get('read_with_scheduled'),
									# "volunteer": match.volunteer,
									# "scheduled_slots": match.scheduled_slots.all(),	
									# "match_active": match.match_active,											
								}
							)
						context['form'] = form

					else:
						form= End_Session_Evaluation_Form(
								initial = {
									"date": timezone.localtime(timezone.now()).date(),
									"completed_by": user,
									# "scheduled_student": scheduled_buddy,
									"read_with_scheduled": False,
									# "volunteer": match.volunteer,
									# "scheduled_slots": match.scheduled_slots.all(),	
									# "match_active": match.match_active,											
								}
							)
						context['form'] = form


				return render(request, "reading_sessions/late_session_evaluation.html", context)
			else:
				return redirect('home')
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')


# Use this one for now
def session_evaluation_view(request, *args, **kwargs):
	print("\n\n\n\nsession_evaluation_view")
	context = {}
	context['page_title'] = "Session Evaluation"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			user_in_rooms = user.room_participants.all()
			# print("session_evaluation", user_in_rooms)
			for old_room in user_in_rooms:		
				# print("In ROOM", old_room, old_room.num_participants, old_room.participants.all())
				old_room.remove_participant(user)
				# print("After ROOM", old_room, old_room.num_participants, old_room.participants)

			context['role'] = user.role.name
			if user.role.name == "Staff" or user.role.name == "Volunteer":
			
			
				user_logs=User_Log.objects.filter(user__role__name="Student", date=timezone.localtime(timezone.now()))
				# print("user_logs", user_logs)
				students=[]
				for item in user_logs:
					if item.user not in students:
						students.append(item.user)


				# students = CustomUser.objects.filter(user_in=user_logs).order_by('full_name')
				context['students'] = students

				reading_levels = Reading_Level.objects.all().order_by('id')
				context['reading_levels'] = reading_levels

				relational_engagement = Relational_Engagement.objects.all().order_by('id')
				context['relational_engagement'] = relational_engagement

				assessment_levels = Evaluation_Level.objects.all().order_by('id')
				context['assessment_levels'] = assessment_levels

				follow_up_types = Follow_Up_Type.objects.all().order_by('id')
				context['follow_up_types'] = follow_up_types

				arrivals = Arrival_Description.objects.all().order_by('id')
				context['arrivals'] = arrivals

			

				if user.role.name == "Volunteer":
					if user.volunteer_profile.match_needed:
						display_scheduled = False
						context['display_scheduled'] = display_scheduled
						context['match_needed'] = user.volunteer_profile.match_needed

					else:
						context['match_needed'] = user.volunteer_profile.match_needed
						if user.session_status.scheduled_buddy:
							display_scheduled = True
							scheduled_buddy = user.session_status.scheduled_buddy
							context['scheduled_buddy'] = scheduled_buddy
							context['display_scheduled'] = display_scheduled

						else:
							display_scheduled = False
							context['display_scheduled'] = display_scheduled

				elif user.role.name == "Staff":
					display_scheduled = False
					context['display_scheduled'] = display_scheduled
					context['match_needed'] = True

				


				

				
					
				

				

				if request.POST:
					form = End_Session_Evaluation_Form(request.POST)
					student = request.POST.get('scheduled_student')
					temp_student = request.POST.get('temp_student')
					# print("STUDENT IN VIEW", student)
					# print("TEMP STUDENT IN VIEW", temp_student)

					# form['scheduled_student']=scheduled_buddy

					if form.is_valid():							
						form.save()

						messages.success(request, 'Session Evaluation Successfully Submitted')
						return redirect("reading_sessions:volunteer_home")
					else:
						if form.errors:
							for field in form:
								for error in field.errors:
									print("Error ", field.name, error)
									if field.name == "read_with_scheduled":
										context['read_with_scheduled_error'] = error

									if field.name == "scheduled_student_attendance":
										context['scheduled_student_attendance_error'] = error

									if field.name == "temp_student":
										context['temp_student_error'] = error


						# print(form.errors)
						# errors = form.errors
						form= End_Session_Evaluation_Form(
							initial = {
								"date": timezone.localtime(timezone.now()).date(),
								"completed_by": user,
								"scheduled_student": scheduled_buddy,
								"read_with_scheduled": request.POST.get('read_with_scheduled'),
								# "volunteer": match.volunteer,
								# "scheduled_slots": match.scheduled_slots.all(),	
								# "match_active": match.match_active,											
							}
						)
						context['form'] = form

						# print("CONTEXT",context)
						# for item in context:
						# 	print(item)
			           
						

				else:
					if display_scheduled:
					
						form= End_Session_Evaluation_Form(
								initial = {
									"date": timezone.localtime(timezone.now()).date(),
									"completed_by": user,
									"scheduled_student": scheduled_buddy,
									# "read_with_scheduled": request.POST.get('read_with_scheduled'),
									# "volunteer": match.volunteer,
									# "scheduled_slots": match.scheduled_slots.all(),	
									# "match_active": match.match_active,											
								}
							)
						context['form'] = form

					else:
						form= End_Session_Evaluation_Form(
								initial = {
									"date": timezone.localtime(timezone.now()).date(),
									"completed_by": user,
									# "scheduled_student": scheduled_buddy,
									"read_with_scheduled": False,
									# "volunteer": match.volunteer,
									# "scheduled_slots": match.scheduled_slots.all(),	
									# "match_active": match.match_active,											
								}
							)
						context['form'] = form


				return render(request, "reading_sessions/session_evaluation.html", context)
			else:
				return redirect('home')
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def not_session_evaluation_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Session Evaluation"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			
			
			user_logs=User_Log.objects.filter(user__role__name="Student", date=timezone.localtime(timezone.now()))
			# print("user_logs", user_logs)
			students=[]
			for item in user_logs:
				if item.user not in students:
					students.append(item.user)


			# students = CustomUser.objects.filter(user_in=user_logs).order_by('full_name')
			context['students'] = students

			reading_levels = Reading_Level.objects.all().order_by('id')
			context['reading_levels'] = reading_levels

			relational_engagement = Relational_Engagement.objects.all().order_by('id')
			context['relational_engagement'] = relational_engagement

			assessment_levels = Evaluation_Level.objects.all().order_by('id')
			context['assessment_levels'] = assessment_levels

			follow_up_types = Follow_Up_Type.objects.all().order_by('id')
			context['follow_up_types'] = follow_up_types

			display_scheduled = True

			if user.role.name == "Volunteer":

				if user.volunteer_profile.match_needed:
					display_scheduled = False


				

				if user.session_status.scheduled_buddy:
					scheduled_buddy = user.session_status.scheduled_buddy
					context['scheduled_buddy'] = scheduled_buddy
					context['display_scheduled'] = display_scheduled
				else:
					display_scheduled = False
					context['display_scheduled'] = display_scheduled

				arrivals = Arrival_Description.objects.all().order_by('id')
				context['arrivals'] = arrivals

				if request.POST:
					form = End_Session_Evaluation_Form(request.POST)
					student = request.POST.get('scheduled_student')
					temp_student = request.POST.get('temp_student')
					# print("STUDENT IN VIEW", student)
					# print("TEMP STUDENT IN VIEW", temp_student)

					# form['scheduled_student']=scheduled_buddy

					if form.is_valid():							
						form.save()

						messages.success(request, 'Session Evaluation Successfully Submitted')
						return redirect("reading_sessions:volunteer_home")
					else:
						if form.errors:
							for field in form:
								for error in field.errors:
									print("Error ", field.name, error)
									if field.name == "read_with_scheduled":
										context['read_with_scheduled_error'] = error

									if field.name == "scheduled_student_attendance":
										context['scheduled_student_attendance_error'] = error

									if field.name == "temp_student":
										context['temp_student_error'] = error


						# print(form.errors)
						# errors = form.errors
						form= End_Session_Evaluation_Form(
							initial = {
								"date": timezone.localtime(timezone.now()).date(),
								"completed_by": user,
								"scheduled_student": scheduled_buddy,
								"read_with_scheduled": request.POST.get('read_with_scheduled'),
								# "volunteer": match.volunteer,
								# "scheduled_slots": match.scheduled_slots.all(),	
								# "match_active": match.match_active,											
							}
						)
						context['form'] = form

						# print("CONTEXT",context)
						# for item in context:
						# 	print(item)
			           
						

				else:
					
					form= End_Session_Evaluation_Form(
							initial = {
								"date": timezone.localtime(timezone.now()).date(),
								"completed_by": user,
								# "scheduled_student": scheduled_buddy,
								# "read_with_scheduled": request.POST.get('read_with_scheduled'),
								# "volunteer": match.volunteer,
								# "scheduled_slots": match.scheduled_slots.all(),	
								# "match_active": match.match_active,											
							}
						)
					context['form'] = form
			
				


				return render(request, "reading_sessions/session_evaluation.html", context)
			else:
				return redirect('home')
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def in_process_session_evaluation_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Session Evaluation"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			
			if user.role.name == "Volunteer":
				user_logs=User_Log.objects.filter(user__role__name="Student", date=timezone.localtime(timezone.now()))
				# print("user_logs", user_logs)
				students=[]
				for item in user_logs:
					if item.user not in students:
						students.append(item.user)


				# students = CustomUser.objects.filter(user_in=user_logs).order_by('full_name')
				context['students'] = students

				reading_levels = Reading_Level.objects.all().order_by('id')
				context['reading_levels'] = reading_levels

				relational_engagement = Relational_Engagement.objects.all().order_by('id')
				context['relational_engagement'] = relational_engagement

				assessment_levels = Evaluation_Level.objects.all().order_by('id')
				context['assessment_levels'] = assessment_levels

				follow_up_types = Follow_Up_Type.objects.all().order_by('id')
				context['follow_up_types'] = follow_up_types

				# display_scheduled = True

				if user.session_status.scheduled_buddy:
					scheduled_buddy = user.session_status.scheduled_buddy
					context['scheduled_buddy'] = scheduled_buddy
					# context['display_scheduled'] = display_scheduled
				# else:
				# 	display_scheduled = False
				# 	context['display_scheduled'] = display_scheduled

				arrivals = Arrival_Description.objects.all().order_by('id')
				context['arrivals'] = arrivals

				if request.POST:
					form = End_Session_Evaluation_Form(request.POST)
					read_with_scheduled = request.POST.get('read_with_scheduled')
					temp_student_assigned = request.POST.get('temp_student_assigned')
					# print("temp_student_assigned", temp_student_assigned)
					# print("TEMP STUDENT IN VIEW", temp_student)

					levels_read_today = request.POST.getlist('level_today')
					context['levels_read_today'] = levels_read_today

					if request.POST.get('temp_student_assigned') == "unknown":
						context['temp_assign_help'] = "Neither"
					else:
						temp_student_assigned = request.POST.get('temp_student_assigned')
						if temp_student_assigned:
							context['temp_assign_help'] = True
						else:
							context['temp_assign_help'] = False

						# print("temp_student_assigned", temp_student_assigned)

					if request.POST.get('level_assessment_performed'):
						context['level_assessment_performed_help'] = True
					else:
						context['level_assessment_performed_help'] = False

					if request.POST.get('follow_up_needed'):
						context['follow_up_needed_help'] = True
					else:
						context['follow_up_needed_help'] = False



					if request.POST.get('read_with_scheduled') == "unknown":
						context['read_with_scheduled_help'] = "Neither"
					else:
						read_with_scheduled_help = request.POST.get('read_with_scheduled')
						if read_with_scheduled_help:
							context['read_with_scheduled_help'] = True
						else:
							context['read_with_scheduled_help'] = False

						# print("read_with_scheduled_help", read_with_scheduled_help)

					if form.is_valid():							
						obj = form.save()
						# obj.level_today.clear()
						# for level in levels_read_today:
						# 	obj.level_today.add(level)

						messages.success(request, 'Session Evaluation Successfully Submitted')
						return redirect("reading_sessions:volunteer_home")
					else:
						if form.errors:
							context['has_errors'] = True
							

							for field in form:
								for error in field.errors:
									# print("Error ", field.name, error)
									if field.name == "read_with_scheduled":
										context['read_with_scheduled_error'] = error
										
										context['read_with_scheduled_help'] = "Neither"

									if field.name == "scheduled_student_attendance":
										context['scheduled_student_attendance_error'] = error
										context['read_with_scheduled_help'] = True

										
									if field.name == "temp_student_assigned":
										context['temp_student_assigned_error'] = error
										context['read_with_scheduled_help'] = False
										

									if field.name == "temp_student":
										context['temp_student_error'] = error
										context['read_with_scheduled_help'] = False

									if field.name == "level_assessment_performed":
										context['level_assessment_performed_error'] = error

										

									if field.name == "assessment_level":
										context['assessment_level_error'] = error

									if field.name == "follow_up_type":
										context['follow_up_type_error'] = error										

									if field.name == "level_today":
										print("*******************")
										context['level_today_error'] = error


										
						else:
							context['has_errors'] = False


						# print(form.errors)
						# errors = form.errors
						if request.POST.get('scheduled_student_attendance'):
							scheduled_student_attendance_choice = int(request.POST.get('scheduled_student_attendance'))
						else:
							scheduled_student_attendance_choice = None
						form= End_Session_Evaluation_Form(
							initial = {
								"date": timezone.localtime(timezone.now()).date(),
								"completed_by": user,
								"scheduled_student": scheduled_buddy,
								"read_with_scheduled": request.POST.get('read_with_scheduled'),
								"temp_student_assigned":request.POST.get('temp_student_assigned'),
								"scheduled_student_attendance":scheduled_student_attendance_choice,
								"books_read":int(request.POST.get('books_read')),
								"level_today":request.POST.getlist('level_today'),

								"session_comment": request.POST.get('session_comment'),
								"social_emotional_learning_comment": request.POST.get('social_emotional_learning_comment'),
								"follow_up_needed": request.POST.get('follow_up_needed'),
								"follow_up_type": request.POST.get('follow_up_type'),
								"follow_up_comment": request.POST.get('follow_up_comment'),
								# "scheduled_slots": match.scheduled_slots.all(),	
								# "match_active": match.match_active,											
							}
						)
						context['form'] = form

						# print("CONTEXT",context)
						# for item in context:
						# 	print(item)
			           
						

				else:
					
					form= End_Session_Evaluation_Form(
							initial = {
								"date": timezone.localtime(timezone.now()).date(),
								"completed_by": user,
								"scheduled_student": scheduled_buddy,
								"read_with_scheduled": request.POST.get('read_with_scheduled'),
								"books_read": 0,
								"follow_up_needed": False
								# "scheduled_slots": match.scheduled_slots.all(),	
								# "match_active": match.match_active,											
							}
						)
					context['form'] = form
			
				


				return render(request, "reading_sessions/session_evaluation.html", context)
			else:
				return redirect('home')
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def hold_session_evaluation_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Session Evaluation"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			
			if user.role.name == "Volunteer":
				user_logs=User_Log.objects.filter(user__role__name="Student", date=timezone.localtime(timezone.now()))
				# print("user_logs", user_logs)
				students=[]
				for item in user_logs:
					if item.user not in students:
						students.append(item.user)


				# students = CustomUser.objects.filter(user_in=user_logs).order_by('full_name')
				context['students'] = students

				reading_levels = Reading_Level.objects.all().order_by('id')
				context['reading_levels'] = reading_levels

				relational_engagement = Relational_Engagement.objects.all().order_by('id')
				context['relational_engagement'] = relational_engagement

				assessment_levels = Evaluation_Level.objects.all().order_by('id')
				context['assessment_levels'] = assessment_levels

				follow_up_types = Follow_Up_Type.objects.all().order_by('id')
				context['follow_up_types'] = follow_up_types

				display_scheduled = True

				if user.session_status.scheduled_buddy:
					scheduled_buddy = user.session_status.scheduled_buddy
					context['scheduled_buddy'] = scheduled_buddy
					context['display_scheduled'] = display_scheduled
				else:
					display_scheduled = False
					context['display_scheduled'] = display_scheduled

				arrivals = Arrival_Description.objects.all().order_by('id')
				context['arrivals'] = arrivals

				if request.POST:
					form = End_Session_Evaluation_Form(request.POST)
					read_with_scheduled = request.POST.get('read_with_scheduled')
					temp_student_assigned = request.POST.get('temp_student_assigned')
					# print("temp_student_assigned", temp_student_assigned)
					# print("TEMP STUDENT IN VIEW", temp_student)

					levels_read_today = request.POST.getlist('level_today')
					context['levels_read_today'] = levels_read_today

					if request.POST.get('temp_student_assigned') == "unknown":
						context['temp_assign_help'] = "Neither"
					else:
						temp_student_assigned = request.POST.get('temp_student_assigned')
						if temp_student_assigned:
							context['temp_assign_help'] = True
						else:
							context['temp_assign_help'] = False

						# print("temp_student_assigned", temp_student_assigned)

					if request.POST.get('level_assessment_performed'):
						context['level_assessment_performed_help'] = True
					else:
						context['level_assessment_performed_help'] = False

					if request.POST.get('follow_up_needed'):
						context['follow_up_needed_help'] = True
					else:
						context['follow_up_needed_help'] = False



					if request.POST.get('read_with_scheduled') == "unknown":
						context['read_with_scheduled_help'] = "Neither"
					else:
						read_with_scheduled_help = request.POST.get('read_with_scheduled')
						if read_with_scheduled_help:
							context['read_with_scheduled_help'] = True
						else:
							context['read_with_scheduled_help'] = False

						# print("read_with_scheduled_help", read_with_scheduled_help)

					if form.is_valid():							
						obj = form.save()
						# obj.level_today.clear()
						# for level in levels_read_today:
						# 	obj.level_today.add(level)

						messages.success(request, 'Session Evaluation Successfully Submitted')
						return redirect("reading_sessions:volunteer_home")
					else:
						if form.errors:
							context['has_errors'] = True
							

							for field in form:
								for error in field.errors:
									# print("Error ", field.name, error)
									if field.name == "read_with_scheduled":
										context['read_with_scheduled_error'] = error
										
										context['read_with_scheduled_help'] = "Neither"

									if field.name == "scheduled_student_attendance":
										context['scheduled_student_attendance_error'] = error
										context['read_with_scheduled_help'] = True

										
									if field.name == "temp_student_assigned":
										context['temp_student_assigned_error'] = error
										context['read_with_scheduled_help'] = False
										

									if field.name == "temp_student":
										context['temp_student_error'] = error
										context['read_with_scheduled_help'] = False

									if field.name == "level_assessment_performed":
										context['level_assessment_performed_error'] = error

										

									if field.name == "assessment_level":
										context['assessment_level_error'] = error

									if field.name == "follow_up_type":
										context['follow_up_type_error'] = error										

									if field.name == "level_today":
										# print("*******************")
										context['level_today_error'] = error


										
						else:
							context['has_errors'] = False


						# print(form.errors)
						# errors = form.errors
						if request.POST.get('scheduled_student_attendance'):
							scheduled_student_attendance_choice = int(request.POST.get('scheduled_student_attendance'))
						else:
							scheduled_student_attendance_choice = None
						form= End_Session_Evaluation_Form(
							initial = {
								"date": timezone.localtime(timezone.now()).date(),
								"completed_by": user,
								"scheduled_student": scheduled_buddy,
								"read_with_scheduled": request.POST.get('read_with_scheduled'),
								"temp_student_assigned":request.POST.get('temp_student_assigned'),
								"scheduled_student_attendance":scheduled_student_attendance_choice,
								"books_read":int(request.POST.get('books_read')),
								"level_today":request.POST.getlist('level_today'),

								"session_comment": request.POST.get('session_comment'),
								"social_emotional_learning_comment": request.POST.get('social_emotional_learning_comment'),
								"follow_up_needed": request.POST.get('follow_up_needed'),
								"follow_up_type": request.POST.get('follow_up_type'),
								"follow_up_comment": request.POST.get('follow_up_comment'),
								# "scheduled_slots": match.scheduled_slots.all(),	
								# "match_active": match.match_active,											
							}
						)
						context['form'] = form

						# print("CONTEXT",context)
						# for item in context:
						# 	print(item)
			           
						

				else:
					
					form= End_Session_Evaluation_Form(
							initial = {
								"date": timezone.localtime(timezone.now()).date(),
								"completed_by": user,
								"scheduled_student": scheduled_buddy,
								"read_with_scheduled": request.POST.get('read_with_scheduled'),
								"books_read": 0,
								"follow_up_needed": False
								# "scheduled_slots": match.scheduled_slots.all(),	
								# "match_active": match.match_active,											
							}
						)
					context['form'] = form
			
				


				return render(request, "reading_sessions/session_evaluation.html", context)
			else:
				return redirect('home')
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def staff_landing_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Staff Home"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			
			if user.role.name == "Staff":

				context=all_user_landing_pages(user, context)
				context=additional_context_all(context, user)
				context['session_lobby']=Room.objects.get(name="Session Lobby")
				context['match_pending']=Room.objects.get(name="Match Pending")
				additional_roles = user.secondary_roles.all()
				context['additional_roles'] = additional_roles
				mega_teams = Mega_Team.objects.all()
				context['mega_teams'] = mega_teams

				coordinator = Secondary_Role.objects.get(name="Coordinator")
				if coordinator in additional_roles:
					is_coordinator = True
					coor_mega_team = Mega_Team.objects.get(coordinator=user)
					context['coor_mega_team']=coor_mega_team
				else:
					is_coordinator = False
				context['is_coordinator'] = is_coordinator


				facilitator = Secondary_Role.objects.get(name="Facilitator")
				if facilitator in additional_roles:
					is_facilitator = True					
				else:
					is_facilitator = False
				context['is_facilitator'] = is_facilitator

				team_leader = Secondary_Role.objects.get(name="Team Leader")
				if team_leader in additional_roles:
					is_team_leader = True
					tl_team = Team.objects.get(leader=user)
					context['tl_team']=tl_team					
				else:
					is_team_leader = False
				context['is_team_leader'] = is_team_leader

				full_access = Secondary_Role.objects.get(name="Full Access")
				if full_access in additional_roles:
					full_access = True					
				else:
					full_access = False
				context['needs_full_access'] = full_access

				# print("Session LobbY", context['session_lobby'].slug)
				# print("match_pending", context['match_pending'].slug)
				# print("orientation_room", context['orientation_room'].slug)
				# server_time = Server_Time.objects.get(active=True)
				# context['server_time'] =server_time
				# context['entry_check'] = entry_check()
				
				
				return render(request, "reading_sessions/staff_landing.html", context)
			else:
				return redirect('home')
		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')


def session_end_view(request, *args, **kwargs):
	print("View in room_left_view")
	context = {}
	context['page_title'] = "Session Ended"

	user = request.user

	if not user.is_authenticated:
		return redirect('login')
	else:
		# user.session_status.manual_redirect_on = False
		# user.session_status.save()
		# if WEB:
		# 	context['debug_mode'] = DEBUG
		# 	context['debug'] = settings.DEBUG
		# else:
		# 	context['debug_mode'] = settings.DEBUG
		# 	context['debug'] = DEBUG
		user_in_rooms = user.room_participants.all()
		# print("session_end_view", user_in_rooms)
		for old_room in user_in_rooms:		
			# print("In ROOM", old_room, old_room.num_participants, old_room.participants.all())
			old_room.remove_participant(user)
			# print("After ROOM", old_room, old_room.num_participants, old_room.participants)


		context['logged_in_user'] = user
		context=additional_context_all(context, user)

		if user.role.name == "Staff":
			if Day_With_Daily_Session.objects.filter(date=timezone.now()).exists():
				day_with_session = Day_With_Daily_Session.objects.get(date=timezone.now())
				context['day_with_session'] = day_with_session	
		elif user.role.name == "Volunteer":
			# return redirect('https://docs.google.com/forms/d/e/1FAIpQLSfLd3mAyoQ9QnQpmMHvZLZU_u90vENyzER7NP3mjvZxosE5Lw/viewform')
			return redirect('reading_sessions:session_evaluation')
		elif user.role.name == "Student":
			pass
		# 	print("\n\nSTAFF")
		# 	day = Day_With_Daily_Session.objects.get(date=timezone.now())
		# 	# day = Day_With_Daily_Session.objects.get(id=1)
		# 	print("day", day)
		# 	context['day_with_sessions'] = day

		return render(request, "reading_sessions/session_ended.html", context)



def ajax_room_reset(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		# get from the client side.	
		user1 = request.user

		# print("*************User room reset", user1 )	
		user_id = request.GET.get("user_id", None)
		# print(user_id)

		# check database.
		if CustomUser.objects.filter(id = user_id).exists():
			user = CustomUser.objects.get(id=user_id)
			user.unread_user.reset_count()
			
			response['valid'] = True
			response['unread_count'] = user.unread_user.unread_count
			return HttpResponse(dumps(response), content_type="application/json")
		else:
			response['valid'] = False
			return HttpResponse(dumps(response), content_type="application/json")

	return JsonResponse({}, status = 400)

def staff_reset_count(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		# get from the client side.		
		user_id = request.GET.get("user_id", None)
		# print(user_id)

		# check database.
		if CustomUser.objects.filter(id = user_id).exists():
			user = CustomUser.objects.get(id=user_id)
			user.unread_staff.reset_count()
			
			response['valid'] = True
			response['unread_staff_count'] = user.unread_staff.unread_count
			return HttpResponse(dumps(response), content_type="application/json")
		else:
			response['valid'] = False
			return HttpResponse(dumps(response), content_type="application/json")

	return JsonResponse({}, status = 400)


# Ajax call to return a private chatroom or create one if does not exist
def create_or_return_private_chat_ajax(request, *args, **kwargs):
	# error = Site_View_Error.objects.create(
	# 							module ="reading_sessions",
	# 							view ="create_or_return_private_chat",
	# 							location_in_view="test",
	# 							occurred_for_user=request.user.username,
	# 							error_text="IN view")
	user1 = request.user
	payload = {}
	if user1.is_authenticated:
		if request.method == "GET":
			user2_id = request.GET.get("user2_id")
			error = Site_View_Error.objects.create(
								module ="reading_sessions",
								view ="create_or_return_private_chat",
								location_in_view="test",
								occurred_for_user=request.user.username,
								error_text=user2_id)
			try:
				try:
					user1 = CustomUser.objects.get(pk=request.user.id)
					user2 = CustomUser.objects.get(pk=user2_id)


					if PrivateChatRoom.objects.get(user1=user1, user2=user2).exists():
						chat = PrivateChatRoom.objects.get(user1=user1, user2=user2)						

						user1_list, created = User_Private_Room_List.objects.get_or_create(user=user1)
						# print(user1_list)
						user1_list.add_room(chat)

						user2_list, created = User_Private_Room_List.objects.get_or_create(user=user2)
						# print(user2_list)
						user2_list.add_room(chat)

						# error = Site_View_Error.objects.create(
						# 			module ="reading_sessions",
						# 			view ="create_or_return_private_chat",
						# 			location_in_view="test",
						# 			occurred_for_user=request.user.username,
						# 			error_text="chat id " + chat.id)

					else:
						chat = PrivateChatRoom.objects.create(user1=user1, user2=user2)
						user1_list, created = User_Private_Room_List.objects.get_or_create(user=user1)
						# print(user1_list)
						user1_list.add_room(chat)

						user2_list, created = User_Private_Room_List.objects.get_or_create(user=user2)
						# print(user2_list)
						user2_list.add_room(chat)

						# error = Site_View_Error.objects.create(
						# 			module ="reading_sessions",
						# 			view ="create_or_return_private_chat",
						# 			location_in_view="test",
						# 			occurred_for_user=request.user.username,
						# 			error_text="chat id " + chat.id)

					payload['response'] = "Successfully got the chat."
					payload['chatroom_id'] = chat.id
					return HttpResponse(dumps(payload), content_type="application/json")

				except Exception as e:
					payload['response'] = e
					return HttpResponse(dumps(payload), content_type="application/json")

			except Exception as e:
				payload['response'] = e
				return HttpResponse(dumps(payload), content_type="application/json")
			
	else:
		payload['response'] = "You can't start a chat if you are not authenticated."
	return HttpResponse(dumps(payload), content_type="application/json")

def ajax_id_new_chat(request):
	response = {}
	# request should be ajax and method should be GET.
	# print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
	if request.is_ajax and request.method == "GET":
		# get from the client side.	
		user1 = request.user

		# print("*************User room reset", user1 )	
		user_2 = request.GET.get("user_id", None)
		# print(user_id)

		# check database.
		if CustomUser.objects.filter(id = user_2).exists():
			user2 = CustomUser.objects.get(id=user_2)
			
			
			response['valid'] = True
			response['user2'] = user2.id

			try:
				if PrivateChatRoom.objects.filter(user1=user1, user2=user2).exists():
					# print("1 exist")
					private_chat = PrivateChatRoom.objects.get(user1=user1, 
															user2=user2)
				elif PrivateChatRoom.objects.filter(user1=user2, user2=user1).exists():
					# print("2 exist")
					private_chat = PrivateChatRoom.objects.get(user1=user2, 
															user2=user1)
				else:
					# print("neither")
					private_chat, created = PrivateChatRoom.objects.get_or_create(user1=user1,
																		user2=user2,
																		last_use=timezone.now())
					# print(private_chat, created, private_chat.id)

				response['private_room_id'] = private_chat.id

				user1_list, created = User_Private_Room_List.objects.get_or_create(user=user1)
				# print(user1_list)
				user1_list.add_room(private_chat)

				user2_list, created = User_Private_Room_List.objects.get_or_create(user=user2)
				# print(user2_list)
				user2_list.add_room(private_chat)
			except Exception as e:
				print(e)
				response['exists'] = "does not exist" + str(e)
				



			return HttpResponse(dumps(response), content_type="application/json")
		else:
			response['valid'] = False
			return HttpResponse(dumps(response), content_type="application/json")

	return JsonResponse({}, status = 400)


def check_room_name(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		# get from the client side.		
		room_name = request.GET.get("room_name", None)
		print("View room_name", room_name)

		# check database.
		if Room.objects.filter(name = room_name).exists():
			response['valid'] = False
			return HttpResponse(dumps(response), content_type="application/json")
		else:
			response['valid'] = True
			room_type = Room_Type.objects.get(letter="C")
			room = Room.objects.create(name=room_name, room_type=room_type)
			response['new_room_id'] = room.id
			return HttpResponse(dumps(response), content_type="application/json")

	return JsonResponse({}, status = 400)


def testing_home_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Testing Home"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			context['role'] = "Staff"
			context['room_name'] = "Example_Room"
			return render(request, "reading_sessions/__testing/testing_home.html", context)

		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')


def testing_staff_view(request, room_name):
	print("ROOM NAME", room_name)
	context = {}
	context['page_title'] = "Staff Member"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			context['role'] = "Staff"
			context['room_name'] = room_name
			token = jwt_token.generateBaseToken("StaffMember","staff@email.com", "Staff")
			context['token']=token
			return render(request, "reading_sessions/__testing/test_staff.html", context)

		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')


def testing_student_view(request, room_name):
	context = {}
	context['page_title'] = "Student Member"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			context['role'] = "Student"
			context['room_name'] = room_name
			token = jwt_token.generateBaseToken("StudentMember","student@email.com", "Student")
			context['token']=token
			return render(request, "reading_sessions/__testing/test_student.html", context)

		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def testing_volunteer_view(request, room_name):
	context = {}
	context['page_title'] = "Volunteer Member"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			context['role'] = "Volunteer"
			context['room_name'] = room_name
			token = jwt_token.generateBaseToken("VolunteerMember","volunteer@email.com", "Volunteer")
			context['token']=token
			return render(request, "reading_sessions/__testing/test_volunteer.html", context)

		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')

def get_drop_for_user(request):
	print("\n\n\n\n************VIEW DROPPING", timezone.now())	
	user = request.user
	response = {}
	if request.method == "GET":
		
		print("user_id", request.GET.get('user_id'))
		print("room", request.GET.get('room_id'))

		user_id =request.GET.get('user_id')
		room_id=request.GET.get('room_id')

		if CustomUser.objects.filter(id=user_id).exists():
			if Room.objects.filter(id=room_id).exists():
				response['valid'] = True
				dropping = CustomUser.objects.get(id=user_id)
				room=Room.objects.get(id=room_id)
				today = timezone.localtime(timezone.now()).date()

				if A_Problem_User.objects.filter(user=dropping, date=today).exists():
					entries = A_Problem_User.objects.filter(user=dropping, date=today)
					for entry in entries:
						if entry != entries.first():
							entry.delete()
						else:
							entry.room = room
							entry.save()
				else:
					entry = A_Problem_User.objects.create(user=dropping, room=room)

				response['dropped'] = user.full_name
			else:
				response['valid'] = False

		else:
			response['valid'] = False

	
	return HttpResponse(dumps(response), content_type="application/json")



def by_jitsi_room_participants_ajax(request):	
	user = request.user
	response = {}
	if request.method == "POST":
		response['valid'] = True
		print("\n\n\n*****IN by_jitsi_room_participants_ajax")
		# print(request.GET)
		print("rooms_str", request.POST.get('rooms_str'))
		# print("Room", request.POST.get('room'))
		# print("Participants String", request.POST.get('participants'))
		rooms=Room.objects.all()
		for room in rooms:
			room.jitsi_participants.clear()
			room.jitsi_num_participants = 0
			room.save()

		room_participants = json.loads(request.POST.get('rooms_str'))
		print("room_participants", room_participants, type(room_participants))

		for key, value in room_participants.items():
			print(key, '->', value)
			room = Room.objects.get(slug=key)
			for item in value:
				print(item)
				user=CustomUser.objects.get(username=item)
				room.jitsi_participants.add(user)
			room.jitsi_num_participants = room.jitsi_participants.all().count()
			room.save()
			
			

		final_rooms = Room.objects.all().order_by('-occupied', 'id');

		payload = {}
		s = LazyJitsiMeetingParticipantsEncoder()
		payload['jitsi_rooms'] = s.serialize(final_rooms)

		data = json.dumps(payload)

		response['rooms'] = data
	
	return HttpResponse(dumps(response), content_type="application/json")


def get_rooms_and_participants(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		# get from the client side.		
		room_name = request.GET.get("room_name", None)
		print("View room_name", room_name)

		rooms = Room.objects.all().order_by('id')	

		payload = {}
		s = LazyJitsiMeetingParticipantsEncoder()
		payload['rooms'] = s.serialize(rooms)

		data = json.dumps(payload)
		response['valid'] = True
		response['rooms'] = data

		
		# # check database.
		# if Room.objects.filter(name = room_name).exists():
		# 	response['valid'] = False
		# 	return HttpResponse(dumps(response), content_type="application/json")
		# else:
		# 	response['valid'] = True
		# 	room_type = Room_Type.objects.get(letter="C")
		# 	room = Room.objects.create(name=room_name, room_type=room_type)
		# 	response['new_room_id'] = room.id
		# 	return HttpResponse(dumps(response), content_type="application/json")

	return HttpResponse(dumps(response), content_type="application/json")


def get_help_requests(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		# get from the client side.		
		all_helps = Help_Request.objects.filter(done=False)
		count= all_helps.count()
		payload = {}

		s = LazyHelpEncoder()
		payload['all_help_requests'] = s.serialize(all_helps)
		payload['help_count'] = count
		data = json.dumps(payload)
		response['valid'] = True

		response['helps'] = data

	return HttpResponse(dumps(response), content_type="application/json")

def create_help_request(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "POST":
		# get from the client side.	
		# print("from user", request.POST.get('from_user_id'))
		# print("from_room ", request.POST.get('from_room_id'))
		# print("message ", request.POST.get('message'))	
		# print("user_message ", request.POST.get('user_message'))		
		from_user=CustomUser.objects.get(id=int(request.POST.get('from_user_id')))
		from_room=Room.objects.get(id=int(request.POST.get('from_room_id')))
		message=request.POST.get('message')
		user_message = request.POST.get('user_message')
		new_request = Help_Request.objects.create(from_user=from_user,
													from_room = from_room,
													message= message,
													user_message = user_message)
		response['valid'] = True

		response['new_help'] = from_room.name + ": " + from_user.username

	return HttpResponse(dumps(response), content_type="application/json")

def ajax_help_mark_as_done(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "POST":
		user_id = request.POST.get('user_id')
		request_id = request.POST.get('request_id')
		send_to_staff = request.POST.get('send_to_staff')

		try:
			user_marking_done = CustomUser.objects.get(id=user_id)
			help_request = Help_Request.objects.get(id=request_id)
			help_request.mark_as_done(user_marking_done.id)
			response['valid'] = True

		except Exception as e:
			print("BROKEN mark_help_request_done", e)
			response['valid'] = False

		

		response['send_to_staff'] = send_to_staff

	return HttpResponse(dumps(response), content_type="application/json")


def ajax_connection_status(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "POST":
		user_id = request.POST.get('user_id')
		room_id = request.POST.get('room_id')
		status_check = request.POST.get('status_check')
		match_check = request.POST.get('match_check')
		staff_check = request.POST.get('staff_check')
		all_connected = json.loads(request.POST.get('all_connected'))
		max_reached = json.loads(request.POST.get('max_reached'))



		try:
			if Room.objects.filter(id=room_id).exists():
				room = Room.objects.get(id=room_id)
				print("Room", room)
			user_for_status= CustomUser.objects.get(id=user_id)
			user_status_ws, created = User_Status.objects.get_or_create(user=user_for_status)
			print("\n\n\nAJAX CONNECTION CHECKS", user_for_status)
			print("all_connected", all_connected)
			print("max_reached", max_reached)
			print("this_count", request.POST.get('this_count'))
			save_user_status = False

			if max_reached:
				today_date_a = timezone.localtime(timezone.now()).date()

				if A_Problem_User.objects.filter(user=user_for_status, date=today_date_a).exists():
					entries = A_Problem_User.objects.filter(user=user_for_status, date=today_date_a)
					for entry in entries:
						if entry != entries.first():
							entry.delete()
						else:
							entry.room = room
							entry.save()
				else:
					entry = A_Problem_User.objects.create(user=user_for_status)

			if user_for_status.status_ws.all_connected != all_connected:
				print("all_connected Not the Same")
				user_for_status.status_ws.all_connected = all_connected
				save_user_status = True

			if user_for_status.status_ws.max_reached != max_reached:
				print(" max_reached Not the Same")
				user_for_status.status_ws.max_reached = max_reached
				save_user_status = True


				

			
			if save_user_status:
				print("Saving")
				user_for_status.status_ws.save()
			else:
				print("No Saving")

			response['has_ws_redirect'] = user_for_status.status_ws.has_ws_redirect
			response['has_status_redirect'] = user_for_status.status_ws.has_status_redirect

			try:
				
				if user_for_status.status_ws.has_status_redirect:
					if user_for_status.status_redirect.to_room:
						status_redirect_room = user_for_status.status_redirect.to_room.id
						response['status_redirect_room'] = status_redirect_room
					else:
						response['status_redirect_room'] = "Initial_Entry"

				else:
					response['status_redirect_room'] = "None"
			except Exception as e:
				print("BROKEN status_redirect_room", e)


			try:
				if user_for_status.role.name == "Staff":
					problem_list = []
					response['staff'] = True
					today = timezone.localtime(timezone.now())
					print("Today", today)
			
					problem_users = A_Problem_User.objects.filter(date=today.date())
					unique_list = []
					print("Problem Users", problem_users)				
					for u in problem_users:
						if u.user not in unique_list:
							unique_list.append(u.user)

					for item in unique_list:
						p_user={}
						p_user['username'] = item.username
						p_user['id'] = item.id
						problem_list.append(p_user)

					

					response['problem_list'] = json.dumps(problem_list)
				else:
					response['staff'] = False
			except Exception as e:
				print("\n\n\n\n\n\n\n\n\nBROKEN Staff Problem", e)
			

			


			response['valid'] = True



		except Exception as e:
			print("BROKEN ajax_connection_status", e)
			response['valid'] = False

		

		# response['send_to_staff'] = send_to_staff

	return HttpResponse(dumps(response), content_type="application/json")



def ajax_get_user_profile(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		# get from the client side.		
		profile_user_id = request.GET.get('profile_to_get')
		print("In View", profile_user_id)
		profiles = []
		try:
			to_get = CustomUser.objects.get(id=int(profile_user_id))
			if to_get.role.name == "Staff":
				profile = to_get.staff_profile
				profiles.append(profile)
			elif to_get.role.name == "Volunteer":
				profile = to_get.volunteer_profile
				profiles.append(profile)
			elif to_get.role.name == "Student":
				profile = to_get.student_profile
				profiles.append(profile)


			print("To Get", to_get)
			print("To Get Profile", profile)
			response['valid'] = True
		except Exception as e:
			response['valid'] = False
		# count= all_helps.count()
		payload = {}

		s = LazyProfileEncoder()
		payload['profiles'] = s.serialize(profiles)

		data = json.dumps(payload)
		

		response['user_profiles'] = data

	return HttpResponse(dumps(response), content_type="application/json")


def ajax_get_student_progress(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		# get from the client side.		
		needed = request.GET.get('needed')
		print("In View needed", needed)
		progress = []
		try:
			# to_get = CustomUser.objects.get(id=int(profile_user_id))
			# if to_get.role.name == "Staff":
			# 	profile = to_get.staff_profile
			# 	profiles.append(profile)
			# elif to_get.role.name == "Volunteer":
			# 	profile = to_get.volunteer_profile
			# 	profiles.append(profile)
			# elif to_get.role.name == "Student":
			# 	profile = to_get.student_profile
			# 	profiles.append(profile)


			# print("To Get", to_get)
			# print("To Get Profile", profile)
			response['valid'] = True
		except Exception as e:
			response['valid'] = False
		# count= all_helps.count()
		payload = {}

		s = LazyStudentProgressEncoder()
		payload['needed'] = s.serialize(progress)

		data = json.dumps(payload)
		

		response['student_progress_reports'] = data

	return HttpResponse(dumps(response), content_type="application/json")


def adjust_user_status(request):
	response = {}
	print("adjusting user status")
	if request.is_ajax and request.method == "POST":
		form_data = request.POST.get('form_data')
		print("request",request)
		print("form_data", form_data)

		# status_check = request.POST.get('status_check')
		# match_check = request.POST.get('match_check')
		# staff_check = request.POST.get('staff_check')



		try:
			adjust_data = json.loads(request.POST.get('form_data'))
			print("adjust_data", adjust_data, type(adjust_data))

			adjust_user = CustomUser.objects.get(id=adjust_data['adjust_user_id'])
			print("Getting the user", adjust_user)

			adjust_room = Room.objects.get(id=adjust_data['adjust_ws_room'])
			print("Getting the room", adjust_room)

			if 'remove_from_websocket' in adjust_data:
				print("Key exists")
				remove_from_websocket_room = adjust_data['remove_from_websocket']
				print("Getting the remove_from_websocket_room", remove_from_websocket_room)
				if remove_from_websocket_room:
					adjust_room.remove_participant(adjust_user)

			for key, value in adjust_data.items():
				print(key, '->', value)
				# user_for_status= CustomUser.objects.get(id=user_id)
			# print("\n\n\nAJAX CONNECTION CHECKS", user_for_status)
			# help_request = Help_Request.objects.get(id=request_id)
			# help_request.mark_as_done(user_marking_done.id)
			response['valid'] = True
			response['adjust_room'] = adjust_room.id
			response['adjust_user'] = adjust_user.id

		except Exception as e:
			print("BROKEN adjust_user_status", e)
			response['valid'] = False

		

		# response['send_to_staff'] = send_to_staff

	return HttpResponse(dumps(response), content_type="application/json")


def ajax_check_room_mismatch(request):
	response = {}
	# request should be ajax and method should be GET.
	if request.is_ajax and request.method == "GET":
		# get from the client side.		
		check_room_id = request.GET.get('room_id')
		print("In View check_room", check_room_id)
		try:
			j_rooms=[]
			room=Room.objects.get(id=check_room_id)
			j_room = Jitsi_Meeting_Room.objects.get(room=room)
			j_room.check_student_alone_mismatch()
			j_rooms.append(j_room)
			payload = {}		

			s = LazyJitsiRoomAndParticipantsEncoder()
			payload['jitsi_room_data'] = s.serialize(j_rooms)

			data = json.dumps(payload)
			print("Data Dump", data)
			response['room_id'] = room.id
			response['room_info'] = data
			response['valid'] = True

		except Exception as e:
			print("Exception ajax_check_room_mismatch", e)
			response['valid'] = False
		

	return HttpResponse(dumps(response), content_type="application/json")