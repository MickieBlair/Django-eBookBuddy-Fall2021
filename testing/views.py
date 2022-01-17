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
from testing import testing_tokens
# Create your views here.


def testing_home_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Testing Home"
	user = request.user
	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			context['role'] = "Staff"
			context['room_name'] = "Example_Room"
			return render(request, "testing/testing_home.html", context)

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
			token = testing_tokens.generateBaseTokenTesting("StaffMember","staff@email.com", "Staff")
			context['token']=token
			return render(request, "testing/test_staff.html", context)

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
			token = testing_tokens.generateBaseTokenTesting("StudentMember","student@email.com", "Student")
			context['token']=token
			return render(request, "testing/test_student.html", context)

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
			token = testing_tokens.generateBaseTokenTesting("VolunteerMember","volunteer@email.com", "Volunteer")
			context['token']=token
			return render(request, "testing/test_volunteer.html", context)

		else:
			return redirect('pending_approval')
	else:		
		return redirect('login')