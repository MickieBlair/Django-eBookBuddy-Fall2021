from reading_sessions.models import Match_Status_Option
from reading_sessions.models import Match_Type
from users.models import Role
from site_admin.models import Note_Category

#Notes
TEMP_MATCH_CREATED = Note_Category.objects.get(name="Temporary Match Created")
TEMP_MATCH_INACTIVE = Note_Category.objects.get(name="Temporary Match Inactive")

#Match Type
TEMP_TYPE = Match_Type.objects.get(name="Temporary")
SCH_TYPE = Match_Type.objects.get(name="Scheduled")

#Match Status OPTIONS
VM = Match_Status_Option.objects.get(name="Volunteer Missing")
SM = Match_Status_Option.objects.get(name="Student Missing")	
VM_SM = Match_Status_Option.objects.get(name="Both Missing")	
VR = Match_Status_Option.objects.get(name="Volunteer Reassigned")
SR = Match_Status_Option.objects.get(name="Student Reassigned")	
VR_SR = Match_Status_Option.objects.get(name="Both Reassigned")
PR = Match_Status_Option.objects.get(name="Pending Redirect")		
IR = Match_Status_Option.objects.get(name="In Room")

#Roles
STUDENT_ROLE = Role.objects.get(name="Student")
VOLUNTEER_ROLE = Role.objects.get(name="Volunteer")
STAFF_ROLE = Role.objects.get(name="Staff")

