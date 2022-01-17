from django.conf import settings
import jwt
from django.utils import timezone
from datetime import datetime
import math

# create a function to generate a token using the pyjwt library

# {
#   "context": {
#     "user": {
#       "avatar": "https:/gravatar.com/avatar/abc123",
#       "name": "John Doe",
#       "email": "jdoe@example.com",
#       "affiliation": "owner"
#     }
#   },
#   "aud": "jitsi",
#   "iss": "mickie-blair-photography",
#   "sub": "reading.sessions-ebookbuddy.org",
#   "room": "*"
# } 
def generateBaseTokenTesting(username, email, role):
	token = "token"
	if role == "Staff":
		affiliation = "owner"
	elif role == "Volunteer":
		affiliation = "moderator"
	elif role == "Student":
		affiliation = "moderator"

	payload = {}
	payload['aud'] = settings.APP_ID
	payload['iss'] = settings.APP_ID
	payload['sub'] = settings.APP_SUB
	payload['exp'] = math.ceil(datetime.timestamp(timezone.now() + timezone.timedelta(hours=4)))
	payload['room'] = "*"
	context = {}
	context['user'] = {
			  "name": username,
			  "email": email,		  
			  "affiliation": affiliation,
			  "session_role": role,
			}

	payload['context'] = context
	# print(payload)

	token = jwt.encode(
		payload, settings.APP_SECRET, algorithm='HS256'
		)
	
	return token


def generateBaseToken(username, email, role, avatar):
	token = "token"
	if role == "Staff":
		affiliation = "owner"
	elif role == "Volunteer":
		affiliation = "moderator"
	elif role == "Student":
		affiliation = "moderator"

	print("username, affiliation", username, affiliation)
	
	payload = {}
	payload['aud'] = settings.APP_ID
	payload['iss'] = settings.APP_ID
	payload['sub'] = settings.APP_SUB
	payload['exp'] = math.ceil(datetime.timestamp(timezone.now() + timezone.timedelta(hours=4)))
	payload['room'] = "*"
	context = {}
	context['user'] = {
			  "name": username,
			  "email": email,
			  "avatar": avatar.url,			  
			  "affiliation": affiliation,
			  "session_role": role,
			}

	payload['context'] = context
	# print(payload)

	token = jwt.encode(
		payload, settings.APP_SECRET, algorithm='HS256'
		)
	
	return token

def generateUserToken(username, email, affiliation):
	token = "token"
	payload = {}
	payload['aud'] = settings.APP_ID
	payload['iss'] = settings.APP_ID
	payload['sub'] = settings.APP_SUB
	payload['exp'] = math.ceil(datetime.timestamp(timezone.now() + timezone.timedelta(hours=4)))
	payload['room'] = "*"
	context = {}
	context['user'] = {
			  "name": username,
			  "email": email,			  
			  "affiliation": affiliation,
			}

	if affiliation == "teacher":		
		context['features'] = {
				  "recording": True,
				  "livestreaming": True,
				  "screen-sharing": True
				}
	else:
		context['features'] = {
				  "recording": False,
				  "livestreaming": False,
				  "screen-sharing": True
				}

	payload['context'] = context
	# print(payload)

	token = jwt.encode(
		payload, settings.APP_SECRET, algorithm='HS256'
		)
	
	return token



def generate_JWT_Token(username, email, user_id):
	token = "token"
	payload = {}
	user_id = username + "_" + str(user_id)
	payload['aud'] = settings.APP_ID
	payload['iss'] = settings.APP_ID
	payload['sub'] = settings.APP_SUB
	payload['exp'] = math.ceil(datetime.timestamp(timezone.now() + timezone.timedelta(hours=12)))
	payload['room'] = "*"
	context = {}
	context['user'] = {
			  "name": username,
			  "email": email,
			  "id": user_id,
			}

	payload['context'] = context
	token = jwt.encode(
		payload, settings.APP_SECRET, algorithm='HS256'
		)
	return token

def statsToken(username, email):
	payload = {}
	payload['aud'] = settings.APP_ID
	payload['iss'] = settings.APP_ID
	payload['sub'] = settings.APP_SUB
	payload['exp'] = math.ceil(datetime.timestamp(timezone.now() + timezone.timedelta(hours=12)))
	payload['room'] = "*"
	payload['admin'] = True
	context = {}
	context['user'] = {
			  "name": username,
			  "email": email,			  
			  "affiliation": "moderator",
			}

	payload['context'] = context
	# print(payload)

	token = jwt.encode(
		payload, settings.APP_SECRET, algorithm='HS256'
		)
	
	return token


