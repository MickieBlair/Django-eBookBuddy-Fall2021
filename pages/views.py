from django.shortcuts import render, redirect
from pages.models import Update_In_Progress

# Create your views here.

# return redirect('update_in_progress')

def home_screen_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Home"

	user = request.user

	if user.is_authenticated:
		context['logged_in_user'] = user
		if user.is_approved:
			if user.role.name == "Staff":
				return redirect('reading_sessions:staff_home')
			elif user.role.name == "Volunteer":
				return redirect('reading_sessions:volunteer_home')
			elif user.role.name == "Student":
				return redirect('reading_sessions:student_home')
				
		else:
			return redirect('pending_approval')
	else:
		return redirect('login')

	return render(request, "pages/home.html", context)

def updating_in_progress_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Update In Progress"

	return render(request, "pages/update_in_progress.html", context)


def pending_approval_view(request, *args, **kwargs):
	context = {}
	context['page_title'] = "Pending Approval"

	user = request.user

	if user.is_authenticated:
		context['logged_in_user'] = user
	else:
		return redirect('login')
	
	return render(request, "pages/pending_approval.html", context)