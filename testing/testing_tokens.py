from django.conf import settings
import jwt
from django.utils import timezone
from datetime import datetime
import math

APP_ID="goebookbuddy"
APP_SUB="reading.goebookbuddy.org"
APP_SECRET="D9E423A3C7AD5E64E7B17BD7B1D34060949A188F8800C4D3157AB5E19F9DE1A19EB561D8BEE578DD0922356B166932E26F33A0C4"

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
	payload['aud'] = APP_ID
	payload['iss'] = APP_ID
	payload['sub'] = APP_SUB
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
		payload, APP_SECRET, algorithm='HS256'
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
	payload['aud'] = APP_ID
	payload['iss'] = APP_ID
	payload['sub'] = APP_SUB
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
		payload, APP_SECRET, algorithm='HS256'
		)
	
	return token

def generateUserToken(username, email, affiliation):
	token = "token"
	payload = {}
	payload['aud'] = APP_ID
	payload['iss'] = APP_ID
	payload['sub'] = APP_SUB
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
		payload, APP_SECRET, algorithm='HS256'
		)
	
	return token



def generate_JWT_Token(username, email, user_id):
	token = "token"
	payload = {}
	user_id = username + "_" + str(user_id)
	payload['aud'] = APP_ID
	payload['iss'] = APP_ID
	payload['sub'] = APP_SUB
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
		payload, APP_SECRET, algorithm='HS256'
		)
	return token

def statsToken(username, email):
	payload = {}
	payload['aud'] = APP_ID
	payload['iss'] = APP_ID
	payload['sub'] = APP_SUB
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
		payload, APP_SECRET, algorithm='HS256'
		)
	
	return token


