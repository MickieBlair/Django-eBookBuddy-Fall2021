from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime
from websockets.utils import calculate_timestamp, calculate_date_time


from rest_framework import serializers
from jitsi_data.models import Jitsi_User_Status
from jitsi_data.models import Jitsi_Meeting_Room
from users.models import CustomUser, Role
from site_admin.models import Room

from django.core.serializers.json import DjangoJSONEncoder


class LazyJitsiUserStatusEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'member_id': int(obj.id)})
		dump_object.update({'username': str(obj.username)})
		dump_object.update({'role': str(obj.role.name)})
		dump_object.update({'full_name': str(obj.full_name)})
		# dump_object.update({'jitsi_id': str(obj.status_jitsi.jitsi_id)})
		dump_object.update({'online': bool(obj.status_jitsi.online)})
		if obj.status_jitsi.room:			
			dump_object.update({'room_id': int(obj.status_jitsi.room.id)})
			dump_object.update({'room_name': str(obj.status_jitsi.room.name)})
		else:
			dump_object.update({'room_id': str(obj.status_jitsi.room)})
			dump_object.update({'room_name': str(obj.status_jitsi.room)})

		dump_object.update({'last_updated': str(calculate_timestamp(obj.status_jitsi.last_updated))})
		# print(dump_object)
		return dump_object

class LazyBaseUserEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'member_id': int(obj.id)})
		dump_object.update({'username': str(obj.username)})
		dump_object.update({'role': str(obj.role.name)})
		dump_object.update({'full_name': str(obj.full_name)})
		# dump_object.update({'jitsi_id': str(obj.status_jitsi.jitsi_id)})
		dump_object.update({'online': bool(obj.status_jitsi.online)})
		if obj.status_jitsi.room:
			dump_object.update({'room_id': int(obj.status_jitsi.room.id)})
			dump_object.update({'room_name': str(obj.status_jitsi.room.name)})
		else:
			dump_object.update({'room_id': str("None")})
			dump_object.update({'room_name': str("None")})
		
		dump_object.update({'last_updated': str(calculate_timestamp(obj.status_jitsi.last_updated))})
		# print(dump_object)
		return dump_object

class LazyJitsiParticipantsEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'member_id': int(obj.id)})
		dump_object.update({'username': str(obj.username)})
		dump_object.update({'role': str(obj.role.name)})
		dump_object.update({'full_name': str(obj.full_name)})
		# dump_object.update({'jitsi_id': str(obj.status_jitsi.jitsi_id)})
		dump_object.update({'online': bool(obj.status_jitsi.online)})
		dump_object.update({'room_id': int(obj.status_jitsi.room.id)})
		dump_object.update({'room_name': str(obj.status_jitsi.room.name)})
		dump_object.update({'last_updated': str(calculate_timestamp(obj.status_jitsi.last_updated))})
		# print(dump_object)
		return dump_object


class LazyJitsiRoomAndParticipantsEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'base_room_id': int(obj.room.id)})
		dump_object.update({'base_room_name': str(obj.room.name)})
		
		dump_object.update({'occupied': bool(obj.occupied)})
		dump_object.update({'count': int(obj.count)})

		dump_object.update({'student_alone': bool(obj.student_alone)})
		dump_object.update({'mismatch': bool(obj.mismatch)})
		dump_object.update({'last_updated': str(calculate_timestamp(obj.last_updated))})
		# print("dump_object", dump_object)
		try:
			participants = obj.participants.all()
			
			s = LazyJitsiParticipantsEncoder()
			dump_object.update({'participants': s.serialize(participants)})
		except Exception as e:
			print("LazyJitsiParticipantsEncoder", e )

		try:
			base_participants = obj.room.participants.all()
			s2 = LazyBaseUserEncoder()
			dump_object.update({'base_participants': s2.serialize(base_participants)})
		except Exception as e:
			print("LazyBaseUserEncoder", e )
		
		

		

		return dump_object
