from django.urls import path

from testing.views import (
	testing_home_view,
	testing_staff_view,
	testing_volunteer_view,
	testing_student_view,
)

app_name = 'testing'

urlpatterns = [

	path('testing_home/', testing_home_view, name="testing_home"),
    path('testing_staff/<room_name>/', testing_staff_view, name="testing_staff"),
    path('testing_student/<room_name>/', testing_student_view, name="testing_student"),
    path('testing_volunteer/<room_name>/', testing_volunteer_view, name="testing_volunteer"),

]