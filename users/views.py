# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from users.forms import Create_User_Form, AccountAuthenticationForm, User_Update_Form
from users.models import Role
from users.models import CustomUser
from pages.models import Update_In_Progress


import json
from json import dumps
from django.http import JsonResponse, HttpResponse

from django.conf import settings
from django.core.mail import send_mail




# Create your views here.
def login_view(request):
	context = {}
	context['page_title'] = "Login"
	context['user_role']= "None"

	updating = Update_In_Progress.objects.filter(updating=True)
	if updating.count() > 0:
		print("Yes, updating")
		updating_now = True
	else:
		print("No, not updating")
		updating_now = False	
	
	if not request.user.is_anonymous:
		user = request.user
		if user.is_authenticated:
			if updating_now:
				if user.is_superuser:
					return redirect('testing:testing_home')
				else:
					return redirect('update_in_progress')
			else:
				if user.role.name == "Staff":
					return redirect('reading_sessions:staff_home')
				elif user.role.name == "Student":
					return redirect('reading_sessions:student_home')
				elif user.role.name == "Volunteer":
					return redirect('reading_sessions:volunteer_home')

	if request.POST:

		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)

			# if not user.role:
			# 	if user.username == "Buddy_Admin" and user.is_superuser:
			# 		student, created = Role.objects.get_or_create(name="Student")
			# 		volunteer, created = Role.objects.get_or_create(name="Volunteer")
			# 		staff, created = Role.objects.get_or_create(name="Staff")	
			# 		user.role = staff
			# 		user.save()


			if user:
				login(request, user)
				if updating_now:
					if user.is_superuser:
						return redirect('testing:testing_home')
					else:
						return redirect('update_in_progress')
				else:
					if user.role:
						role = Role.objects.get(id=user.role.id)
						print("Role....", role)
						
						if role.name == "Staff":
							return redirect('reading_sessions:staff_home')
						elif role.name == "Student":
							return redirect('reading_sessions:student_home')
						elif role.name == "Volunteer":
							return redirect('reading_sessions:volunteer_home')
					else:
						print("No Role")
						from_user = str(settings.SERVER_EMAIL)
						to_user = 'admin@ebookbuddy.org'
						subject = "Login Error" + " - " + user.username
						message = user.username + "-" + user.full_name
						print(from_user, to_user)
						send_mail(
							subject,
							message,
							from_user,
							[to_user,],
							fail_silently=False,
							)
						return redirect('logout')


					# try:
					# 	role =
					# 	if user.role.name == "Staff":
					# 		return redirect('reading_sessions:staff_home')
					# 	elif user.role.name == "Student":
					# 		return redirect('reading_sessions:student_home')
					# 	elif user.role.name == "Volunteer":
					# 		return redirect('reading_sessions:volunteer_home')
					# except Exception as e:
					# 	print("Exception", e)
					# 	
					

		else:
			if updating_now:
				return redirect('update_in_progress')

	else:
		form = AccountAuthenticationForm()

	context['login_form'] = form

	return render(request, "users/login.html", context)


def logout_view(request):
	print("Logging out")
	logout(request)
	return redirect('/')


def registration_view(request):
	context = {}
	context['page_title'] = "Register"

	# user = request.user

	# roles = Role.objects.all()
	# context['roles'] = roles

	# if user.is_admin:

	# 	if request.POST:
	# 		form = Create_User_Form(request.POST)
	# 		if form.is_valid():
	# 			print(request.POST.get('role'))
	# 			form.save()
	# 			email = form.cleaned_data.get('email').lower()
	# 			username = form.cleaned_data.get('username').lower()
	# 			raw_password = form.cleaned_data.get('password1')
	# 			account = authenticate(username=username, password=raw_password)
	# 			print(account)
	# 			room = Room.objects.get(room_type = "I")
	# 			location = User_Room_Location.objects.create(user=account, room=room)
	# 			room.add_participant(account)
	# 			# return redirect('reading_sessions:main_room')

	# 		else:
	# 			print(form.errors)
	# 			context['registration_form'] = form

	# 	else:
	# 		form = Create_User_Form()
	# 		context['registration_form'] = form
	# 	return render(request, 'users/register.html', context)

	# else:
	# 	return redirect('home')
	return render(request, 'users/access_denied.html', {})


def must_authenticate_view(request):
    return render(request, 'users/must_authenticate.html', {})

def denied_view(request):
    return render(request, 'users/access_denied.html', {})

def login_as_different_user(request):
    logout(request)
    return redirect('login')




#AJAX CALLS INTERNAL
def email_check(request):
  response = {}
  # request should be ajax and method should be GET.
  if request.is_ajax and request.method == "GET":
    # get from the client side.   
    email = request.GET.get("target_id", None)

    # check database.
    if CustomUser.objects.filter(email = email).exists():
      response['valid'] = True
      
      return HttpResponse(dumps(response), content_type="application/json")
    else:
      response['valid'] = False
      return HttpResponse(dumps(response), content_type="application/json")

  return JsonResponse({}, status = 400)

def account_view(request, *args, **kwargs):
	context = {}
	user_id = kwargs.get("user_id")
	try:
		account = Account.objects.get(pk=user_id)
	except:
		return HttpResponse("Something went wrong.")

	return render(request, "account/account.html", context)