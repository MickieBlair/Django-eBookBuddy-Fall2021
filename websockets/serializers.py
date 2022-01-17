from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime
from websockets.utils import calculate_timestamp, calculate_date_time
from websockets.staff_chat_constants import *
from websockets.room_chat_constants import *
from websockets.private_chat_constants import *

from websockets.models import UnreadChatRoomMessages

class LazyStudentProgressEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'student_id': int(obj.user.id)})
		dump_object.update({'username': str(obj.user.username)})
		dump_object.update({'full_name': str(obj.user.full_name)})
		if obj.initial_assessment:
			dump_object.update({'has_assessment': str("Yes")})
		else:
			dump_object.update({'has_assessment': str("No")})

		dump_object.update({'starting': str(obj.starting)})
		dump_object.update({'current': str(obj.current)})
		dump_object.update({'last_assessed': str(obj.last_assessed)})

		# print(dump_object)
		return dump_object

class LazyProfileEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'member_id': int(obj.user.id)})
		dump_object.update({'username': str(obj.user.username)})
		dump_object.update({'role': str(obj.user.role.name)})
		dump_object.update({'full_name': str(obj.user.full_name)})
		dump_object.update({'email': str(obj.user.email)})

		session_status = obj.user.session_status
		
		if obj.user.role.name == "Staff":
			profile = obj.user.staff_profile
			dump_object.update({'phone': str(profile.contact_number)})
			dump_object.update({'match_needed': str("No")})
			dump_object.update({'scheduled_buddy': str("None")})
			dump_object.update({'gender': str(profile.gender)})
			dump_object.update({'p_lang': str(profile.primary_lang)})
			dump_object.update({'s_lang': str(profile.secondary_lang)})
			dump_object.update({'created': calculate_timestamp(profile.date_created)})
			dump_object.update({'updated': calculate_timestamp(profile.last_updated)})
		elif obj.user.role.name == "Volunteer":
			profile = obj.user.volunteer_profile
			dump_object.update({'phone': str(profile.contact_number)})
			if profile.match_needed:
				match_str = "Yes"
				sch_buddy_str = dump_object.update({'scheduled_buddy': str("None")})
			else:
				match_str = "No"
				sch_buddy_str = dump_object.update({'scheduled_buddy': str(session_status.scheduled_match.student.full_name)})
			dump_object.update({'match_needed': str(match_str)})
			dump_object.update({'gender': str(profile.gender)})
			dump_object.update({'p_lang': str(profile.primary_lang)})
			dump_object.update({'s_lang': str(profile.secondary_lang)})
			dump_object.update({'created': calculate_timestamp(profile.date_created)})
			dump_object.update({'updated': calculate_timestamp(profile.last_updated)})
			if profile.scheduled_day_time_slots.all().count() != 0:
				slots = profile.scheduled_day_time_slots.all()
				s = LazySessionSlotEncoder()
				dump_object.update({'slots': s.serialize(slots)})
			else:
				dump_object.update({'slots': str("No Scheduled Slots")})
				



		elif obj.user.role.name == "Student":
			profile = obj.user.student_profile
			dump_object.update({'phone': str(profile.contact_number)})
			dump_object.update({'person': str(profile.contact_person)})
			if profile.match_needed:
				match_str = "Yes"
				sch_buddy_str = dump_object.update({'scheduled_buddy': str("None")})
			else:
				match_str = "No"
				sch_buddy_str = dump_object.update({'scheduled_buddy': str(session_status.scheduled_match.volunteer.full_name)})
			dump_object.update({'match_needed': str(match_str)})
			dump_object.update({'gender': str(profile.gender)})
			dump_object.update({'p_lang': str(profile.primary_lang)})
			dump_object.update({'s_lang': str(profile.secondary_lang)})
			dump_object.update({'school': str(profile.school)})
			dump_object.update({'grade': str(profile.grade)})
			dump_object.update({'created': calculate_timestamp(profile.date_created)})
			dump_object.update({'updated': calculate_timestamp(profile.last_updated)})

			if profile.scheduled_day_time_slots.all().count() != 0:
				slots = profile.scheduled_day_time_slots.all()
				s = LazySessionSlotEncoder()
				dump_object.update({'slots': s.serialize(slots)})
			else:
				dump_object.update({'slots': str("No Scheduled Slots")})

		
		# print(dump_object)
		return dump_object

class LazySessionSlotEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'slot': str(obj.get_name_time())})
		# print(dump_object)
		return dump_object

class LazyMatchStatusEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'match_status_id': int(obj.id)})
		dump_object.update({'get_type': str(obj.get_type())})
		dump_object.update({'match_status_active': bool(obj.match_status_active)})
		dump_object.update({'session_id': int(obj.session.id)})
		dump_object.update({'session_slot': str(obj.session.day_time.session_slot)})
		dump_object.update({'student_id': int(obj.get_student().id)})
		dump_object.update({'student_online': bool(obj.get_student().session_status.logged_in)})
		dump_object.update({'display_student_location': bool(obj.display_student_location)})
		dump_object.update({'buddy_id': int(obj.get_buddy().id)})
		dump_object.update({'buddy_online': bool(obj.get_buddy().session_status.logged_in)})
		dump_object.update({'display_buddy_location': bool(obj.display_buddy_location)})
		if obj.get_student().session_status.room:
			dump_object.update({'student_location': str(obj.get_student().session_status.room.id)})
		if obj.get_buddy().session_status.room:
			dump_object.update({'teacher_location': str(obj.get_buddy().session_status.room.id)})

		if(obj.match_type):
			dump_object.update({'match_type': str(obj.match_type.name)})
		else:
			dump_object.update({'match_type': "Broken"})
		dump_object.update({'complete': bool(obj.both_online)})
		dump_object.update({'status': str(obj.status.name)})
		if obj.match_type.name == "Temporary":
			dump_object.update({'student_username': str(obj.temp_match.student_user.username)})
			dump_object.update({'student_full_name': str(obj.temp_match.student_user.full_name)})
			# if obj.temp_match.student_user.session_status.room:
			# 	dump_object.update({'student_location': str(obj.temp_match.student_user.session_status.room.id)})
			dump_object.update({'teacher_username': str(obj.temp_match.teacher_user.username)})
			dump_object.update({'teacher_full_name': str(obj.temp_match.teacher_user.full_name)})
			# if obj.temp_match.teacher_user.session_status.room:
			# 	dump_object.update({'teacher_location': str(obj.temp_match.teacher_user.session_status.room.id)})


		# print(dump_object)
		return dump_object

class LazySessionStatusEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'member_id': int(obj.user.id)})
		dump_object.update({'username': str(obj.user.username)})
		dump_object.update({'role': str(obj.user.role.name)})
		dump_object.update({'full_name': str(obj.user.full_name)})
		dump_object.update({'needs_match': bool(obj.needs_session_match)})
		# print(dump_object)
		return dump_object

class LazyHelpEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'request_id': int(obj.id)})
		dump_object.update({'from_user_id': int(obj.from_user.id)})
		dump_object.update({'username': str(obj.from_user.username)})
		dump_object.update({'full_name': str(obj.from_user.full_name)})
		dump_object.update({'from_room_id': int(obj.from_room.id)})
		dump_object.update({'from_room': str(obj.from_room.name)})
		dump_object.update({'from_room_slug': str(obj.from_room.slug)})
		dump_object.update({'created': calculate_timestamp(obj.created)})
		dump_object.update({'message': str(obj.message)})
		dump_object.update({'user_message': str(obj.user_message)})
		dump_object.update({'room_url': str(obj.room_url)})
		dump_object.update({'done': bool(obj.done)})
		if obj.visited_by:
			dump_object.update({'visited_by_id': int(obj.visited_by.id)})
			dump_object.update({'visited_by_username': str(obj.visited_by.username)})
			dump_object.update({'visited_by_full_name': str(obj.visited_by.full_name)})
			dump_object.update({'visited_time': calculate_timestamp(obj.visited_time)})
		# print(dump_object)
		return dump_object


class LazyRedirectEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'redirect_id': int(obj.id)})
		dump_object.update({'user_to_redirect_id': int(obj.user_to_redirect.id)})
		dump_object.update({'user_to_redirect_name': str(obj.user_to_redirect.full_name)})
		dump_object.update({'to_room_id': int(obj.to_room.id)})
		dump_object.update({'to_room_name': str(obj.to_room.name)})
		dump_object.update({'to_room_slug': str(obj.to_room.slug)})
		dump_object.update({'redirect_url': str(obj.redirect_url)})
		return dump_object

class LazyPrivateRoomEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'private_room_id': int(obj.id)})
		dump_object.update({'user1_id': int(obj.user1.id)})
		dump_object.update({'user1_name': str(obj.user1.full_name)})
		dump_object.update({'user1_unread': int(obj.unread_count_by_user(obj.user1))})
		dump_object.update({'user2_id': int(obj.user2.id)})
		dump_object.update({'user2_name': str(obj.user2.full_name)})
		dump_object.update({'user2_unread': int(obj.unread_count_by_user(obj.user2))})
		dump_object.update({'total': int(obj.total_message_count())})

		return dump_object

class LazyRoomParticipantsEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'room_id': int(obj.id)})
		dump_object.update({'room_name': str(obj.name)})
		dump_object.update({'room_slug': str(obj.slug)})
		dump_object.update({'room_row': "room_" + str(obj.id)})
		dump_object.update({'occupied': bool(obj.occupied)})
		dump_object.update({'count': int(obj.num_participants)})
		participants = obj.participants.all()
		s = LazyMeetingParticipantsEncoder()
		dump_object.update({'participants': s.serialize(participants)})
		return dump_object


class LazyMeetingParticipantsEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'member_id': str(obj.id)})
		dump_object.update({'username': str(obj.username)})
		dump_object.update({'role': str(obj.role.name)})
		dump_object.update({'full_name': str(obj.full_name)})
		dump_object.update({'needs_match': bool(obj.session_status.needs_session_match)})
		# print(dump_object)
		return dump_object

class LazyRoomUnreadEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'userID': int(obj.id)})
		if obj.unread_user:
			dump_object.update({'unread_count': int(obj.unread_user.unread_count)})

		# print(dump_object)
		return dump_object
		
class LazyJitsiRoomChatMessageEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'msg_type': JITSI_MSG_TYPE_MESSAGE})
		dump_object.update({'msg_id': int(obj.id)})
		dump_object.update({'user_id': int(obj.user.id)})
		dump_object.update({'username': str(obj.user.username)})
		dump_object.update({'full_name': str(obj.user.full_name)})
		dump_object.update({'message': str(obj.content)})
		dump_object.update({'meeting_room_id': int(obj.meeting_room.id)})
		dump_object.update({'meeting_room_name': str(obj.meeting_room.name)})
		dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
		dump_object.update({'date_time': calculate_date_time(obj.timestamp)})
		dump_object.update({'display': bool(obj.display)})
		return dump_object


class LazyStaffRoomChatMessageEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'msg_type': STAFF_MSG_TYPE_MESSAGE})
		dump_object.update({'msg_id': int(obj.id)})
		dump_object.update({'user_id': int(obj.user.id)})
		dump_object.update({'username': str(obj.user.username)})
		dump_object.update({'full_name': str(obj.user.full_name)})
		dump_object.update({'message': str(obj.content)})
		dump_object.update({'meeting_room_id': int(obj.meeting_room.id)})
		dump_object.update({'meeting_room_name': str(obj.meeting_room.name)})
		dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
		dump_object.update({'date_time': calculate_date_time(obj.timestamp)})
		return dump_object



class LazyStaffEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'userID': int(obj.id)})
		dump_object.update({'staff_unread_count': int(obj.unread_staff.unread_count)})


		# print(dump_object)
		return dump_object

class LazyPrivateRoomChatMessageEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'msg_type': PRIVATE_MSG_TYPE_MESSAGE})
		dump_object.update({'msg_id': str(obj.id)})
		dump_object.update({'user_id': str(obj.user.id)})
		dump_object.update({'username': str(obj.user.username)})
		if obj.user.session_status.room:
			dump_object.update({'in_room_id': str(obj.user.session_status.room.id)})
			dump_object.update({'in_room_name': str(obj.user.session_status.room.name)})
			dump_object.update({'in_room_slug': str(obj.user.session_status.room.slug)})
		dump_object.update({'message': str(obj.content)})
		dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
		return dump_object


class LazyCustomUserEncoder(Serializer):
	def get_dump_object(self, obj):
		# print(obj.session_status.room)
		dump_object = {}
		dump_object.update({'user_id': str(obj.id)})
		dump_object.update({'username': str(obj.username)})
		dump_object.update({'role': str(obj.role.name)})
		dump_object.update({'full_name': str(obj.full_name)})
		if obj.session_status.room:
			dump_object.update({'location_id': str(obj.session_status.room.id)})	
			dump_object.update({'location_name': str(obj.session_status.room.name)})	
			dump_object.update({'location_slug': str(obj.session_status.room.slug)})	
		# print(dump_object)
		return dump_object



class LazyJitsiMeetingParticipantsEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'room_id': int(obj.id)})
		dump_object.update({'room_name': str(obj.name)})
		dump_object.update({'occupied': bool(obj.occupied)})
		dump_object.update({'count': int(obj.num_participants)})
		dump_object.update({'jitsi_count': int(obj.jitsi_num_participants)})
		participants = obj.participants.all()
		s = LazyMeetingParticipantsEncoder()
		dump_object.update({'participants': s.serialize(participants)})

		jitsi_participants = obj.jitsi_participants.all()
		s = LazyMeetingParticipantsEncoder()
		dump_object.update({'jitsi_participants': s.serialize(jitsi_participants)})


		return dump_object