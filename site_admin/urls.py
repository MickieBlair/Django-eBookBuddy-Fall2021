from django.urls import path

from site_admin.views import (
    admin_home_view,

    #superuser
    superuser_home_view,
    create_initial_data_view,
    create_team_meetings_view,
    upload_students,
    upload_volunteers,
    upload_staff,
    create_avatars_view,
    process_session_evaluations_view,
    
    #users
    users_by_role_view,
    create_user_view,
    edit_user_view,
    view_profile_view,
    edit_staff_profile_view,
    edit_volunteer_profile_view,
    edit_student_profile_view,

    #semesters
    all_semesters_view,
    create_semester_view,
    make_semester_active,
    edit_semester_view,

    #sessions
    create_day_time_slot_view,
    all_day_time_slots_view,
    edit_day_time_slot_view,
    make_slot_active,
    sessions_by_semester_view,
    create_sessions_for_semester_view,
    edit_sessions_for_semester_view,
    days_with_sessions_by_semester_view,

    #rooms
    all_rooms_view,
    create_custom_room_view,
    create_additional_breakout_rooms_view,

    #matches
    scheduled_matches_view,
    create_match_for_semester_view,
    edit_match_view,
    sessions_by_match_view,

    #staff
    staff_mark_day_as_complete_view,

    #reports
    all_students_attendance_report_view,
    individual_student_attendance_report_view,
    download_student_report,
    all_volunteers_attendance_report_view,
    individual_volunteer_attendance_report_view,
    download_volunteer_report,
    attendance_by_session_view,
    attendance_by_day_view,
    all_days_attendance_reports_view,
    all_session_evaluations_reports_view,
    download_evaluation_report,
    assessments_view,
    download_assessments_report,
    users_signs_ins_view,
    process_all_sign_ins_view,
    individual_time_logs_view,
    all_logs_view,
    download_time_log_individual_report,
    download_time_log_report_by_role,


    #AJAX INTERNAL
    approve_user,
    ajax_search_users,

    )


    # #session
    # all_sessions_view,

    # #users
    # all_users_view,
    # 
    # 
    # view_student_profile_view,
    # edit_student_profile_view,
    # view_volunteer_profile_view,
    # edit_volunteer_profile_view,

    # #AJAX INTERNAL
    # approve_user,
    # mark_session_complete,


    

    # #matches
    # all_scheduled_matches_view,
    # all_scheduled_matches_by_semester_view,
    # active_scheduled_matches_by_semester_view,
    # archived_scheduled_matches_by_semester_view,

    # match_attendance_view,
    # match_notes_view,
    # all_scheduled_matches_by_session_view,
    # active_scheduled_matches_by_session_view,
    # archived_scheduled_matches_by_session_view,
    

    
    # #csv
    # get_attendance_by_session_csv,
    # get_attendance_by_day_csv,
    # # by_session_attendance_csv,
    # # by_todays_sessions_csv,

    # #reports
    # all_days_attendance_reports_view,
    # staff_mark_day_as_complete_view,
    # attendance_by_session_view,
    # attendance_by_day_view,
    # end_student_attendance_view,
    # student_attendance_report_view,
    # get_semester_student_report_csv,
    # end_volunteer_attendance_view,
    # volunteer_attendance_report_view,
    # get_semester_volunteer_report_csv,

    # # 
    # # all_student_applications_view,
    # # review_student_application_view,
    # # # user_list,
    # # make_adjustments_sessions,
    # # add_scheduled_matches,
    # # create_attendance,
    # # 
 # )


app_name = 'site_admin'

urlpatterns = [
    path('', admin_home_view, name="admin_home"),
    

    #users
    path('users/<role_name>/', users_by_role_view, name="users"),
    path('user/create/', create_user_view, name="create_user"),
    path('edit_user/<user_id>/', edit_user_view, name="edit_user"),
    path('user_profile/<user_id>/', view_profile_view, name="user_profile"),
    path('user_profile/staff/edit/<user_id>/', edit_staff_profile_view, name="edit_staff_profile"),
    path('user_profile/student/edit/<user_id>/', edit_student_profile_view, name="edit_student_profile"),
    path('user_profile/volunteer/edit/<user_id>/', edit_volunteer_profile_view, name="edit_volunteer_profile"),

    #semesters
    path('semesters/', all_semesters_view, name="semesters"),
    path('semester/create/', create_semester_view, name="create_semester"),
    path('semester/active/<semester_id>/', make_semester_active, name="make_semester_active"),
    path('semester/edit/<semester_id>/', edit_semester_view, name="edit_semester"),

    #superuser
    path('superuser_home/', superuser_home_view, name="superuser_home"),    
    path('superuser_home/initial_data/', create_initial_data_view, name="initial_data"),
    path('superuser_home/upload_students/', upload_students, name="upload_students"),
    path('superuser_home/upload_volunteers/', upload_volunteers, name="upload_volunteers"),
    path('superuser_home/upload_staff/', upload_staff, name="upload_staff"),
    path('superuser_home/team_meetings/', create_team_meetings_view, name="team_meetings"),
    path('superuser_home/create_avatars/', create_avatars_view, name="create_avatars"),
    path('superuser_home/process_evaluations/', process_session_evaluations_view, name="process_evaluations"),
    path('superuser_home/process_all_sign_ins/<role_name>/', process_all_sign_ins_view, name="process_all_sign_ins"),

    #sessions
    path('create_day_time_slot/', create_day_time_slot_view, name="create_day_time_slot"),
    path('day_time_slots/', all_day_time_slots_view, name="day_time_slots"),
    path('day_time_slots/<entry_id>/', edit_day_time_slot_view, name="edit_day_time_slot"),
    path('day_time_slots/make_active/<entry_id>/', make_slot_active, name="activate_slot"),
    path('sessions_by_semester/<semester_id>/<order_by>/', sessions_by_semester_view, name="sessions_by_semester"),
    path('sessions_by_day/<semester_id>/<order_by>/', days_with_sessions_by_semester_view, name="sessions_by_day"),
    path('create_sessions/<semester_id>/', create_sessions_for_semester_view, name="create_sessions"),
    path('edit_sessions/<semester_id>/', edit_sessions_for_semester_view, name="edit_sessions"),


    #rooms
    path('rooms/', all_rooms_view, name="all_rooms"),
    path('rooms/create_custom/', create_custom_room_view, name="create_custom_room"),
    path('rooms/create_breakouts/', create_additional_breakout_rooms_view, name="create_breakout_rooms"),

    #matches
    path('scheduled_matches/<semester_id>/<by_call>/<by_type>/', scheduled_matches_view, name="scheduled_matches"),
    path('scheduled_matches/create/<semester_id>/', create_match_for_semester_view, name="create_match_for_semester"),
    path('scheduled_matches/edit/<match_id>/', edit_match_view, name="edit_match"),
    path('scheduled_matches/sessions/<match_id>/', sessions_by_match_view, name="match_sessions"),

    #staff
    path('reports/day_complete/<day_id>/', staff_mark_day_as_complete_view, name="staff_mark_day_complete"),

    #reports
    path('reports/attendance/', all_days_attendance_reports_view, name="all_days_attendance_reports"),
    path('reports/all_students_attendance/', all_students_attendance_report_view, name="all_students_attendance_report"),
    path('reports/student_attendance/<user_id>/', individual_student_attendance_report_view, name="individual_student_attendance"),
    path('reports/download/student_attendance/', download_student_report, name="download_all_students"),
    path('reports/download/evaluations/', download_evaluation_report, name="download_evaluation_report"),
    
    path('reports/all_volunteers_attendance/', all_volunteers_attendance_report_view, name="all_volunteers_attendance_report"),
    path('reports/volunteer_attendance/<user_id>/', individual_volunteer_attendance_report_view, name="individual_volunteer_attendance"),
    path('reports/download/volunteer_attendance/', download_volunteer_report, name="download_all_volunteers"),
    path('reports/session_evaluations/', all_session_evaluations_reports_view, name="all_session_evaluations"),
    path('reports/assessments/', assessments_view, name="assessments"),
    path('reports/download/assessments/', download_assessments_report, name="download_assessments_report"),
    path('reports/all_sign_ins/<role_name>/', users_signs_ins_view, name="all_sign_ins"),
    path('reports/individual_logs/<user_id>/', individual_time_logs_view, name="individual_logs"),
    path('reports/all_logs/', all_logs_view, name="all_logs"),
    path('attendance_by_session/<session_id>/', attendance_by_session_view, name="attendance_by_session"),
    path('attendance_by_day/<day_id>/', attendance_by_day_view, name="attendance_by_day"),
    path('reports/user_logs/<member_id>/', download_time_log_individual_report, name="individual_log"),
    path('reports/user_logs_by_role/<role>/', download_time_log_report_by_role, name="by_role_logs"),

    
    #AJAX INTERNAL
    path('get/ajax/approve/user', approve_user, name = "approve_user"),
    path('get/ajax/search/users', ajax_search_users, name = "ajax_search_users"),

    

    # #sessions
    # path('sessions/all/', all_sessions_view, name="all_sessions"),
    # path('sessions_by_semester/<semester_id>/<order_by>/', sessions_by_semester_view, name="sessions_by_semester"),
    # path('create_sessions/<semester_id>/', create_sessions_for_semester_view, name="create_sessions"),
    # 
    # #users
    # path('users/', all_users_view, name="users"),
    # 
    # 
    # path('student_profile/<user_id>/', view_student_profile_view, name="view_student_profile"),
    # path('student_profile/<user_id>/edit/', edit_student_profile_view, name="edit_student_profile"),
    # path('volunteer_profile/<user_id>/', view_volunteer_profile_view, name="view_volunteer_profile"),
    # path('volunteer_profile/<user_id>/edit/', edit_volunteer_profile_view, name="edit_volunteer_profile"),

    # #AJAX INTERNAL
    # path('get/ajax/approve/user', approve_user, name = "approve_user"),
    # path('get/ajax/mark_session_complete/session', mark_session_complete, name = "mark_session_complete"),



    # #matches
    # path('scheduled_matches/', all_scheduled_matches_view, name="scheduled_matches"),
    # path('semester_scheduled_matches/<semester_id>/', all_scheduled_matches_by_semester_view, name="all_semester_scheduled_matches"),
    # path('active_semester_scheduled_matches/<semester_id>/', active_scheduled_matches_by_semester_view, name="active_semester_scheduled_matches"),
    # path('archived_semester_scheduled_matches/<semester_id>/', archived_scheduled_matches_by_semester_view, name="archived_semester_scheduled_matches"),
   
    # 
    # path('match_attendance/<match_id>/', match_attendance_view, name="match_attendance"),
    # path('match_notes/<match_id>/', match_notes_view, name="match_notes"),
    # path('session_scheduled_matches/<session_id>/', all_scheduled_matches_by_session_view, name="all_session_scheduled_matches"),
    # path('active_session_scheduled_matches/<session_id>/', active_scheduled_matches_by_session_view, name="active_session_scheduled_matches"),
    # path('archived_session_scheduled_matches/<session_id>/', archived_scheduled_matches_by_session_view, name="archived_session_scheduled_matches"),
    
    
    # #csv
    # path('session_attendance_csv/<session_id>/', get_attendance_by_session_csv, name="by_session_attendance_csv"),
    # path('day_attendance_csv/<day_id>/', get_attendance_by_day_csv, name="by_day_attendance_csv"),

    # #reports
    # path('reports/attendance/', all_days_attendance_reports_view, name="all_days_attendance_reports"),
    # path('reports/day_complete/<day_id>/', staff_mark_day_as_complete_view, name="staff_mark_day_complete"),
    # path('attendance_by_session/<session_id>/', attendance_by_session_view, name="attendance_by_session"),
    # path('attendance_by_day/<day_id>/', attendance_by_day_view, name="attendance_by_day"),
    # path('reports/attendance/volunteers/', end_volunteer_attendance_view, name="end_volunteer"),
    # path('reports/attendance/students/', end_student_attendance_view, name="end_student"),
    # path('reports/individual_volunteer/attendance/<volunteer_id>/', volunteer_attendance_report_view, name="volunteer_attendance"),
    # path('reports/volunteer/attendance/<semester_id>/', get_semester_volunteer_report_csv, name="semester_volunteer_report"),
    # path('reports/individual_student/attendance/<student_id>/', student_attendance_report_view, name="student_attendance"),
    # path('reports/student/attendance/<semester_id>/', get_semester_student_report_csv, name="semester_student_report"),

  
    # # path('all_student_applications/', all_student_applications_view, name="all_student_applications"),
    # # path('student_application/<app_id>/', review_student_application_view, name="student_app"),
    # # path('sessions/all/', all_sessions_view, name="all_sessions"),
    # # # path('user_list/', user_list, name="user_list"),
    # # path('session_adjustments/', make_adjustments_sessions, name="session_adjustments"),
    # # path('add_scheduled_matches/', add_scheduled_matches, name="add_scheduled_matches"),
    # # path('create_attendance/', create_attendance, name="create_attendance"),
    # # path('superuser_home/', superuser_home_view, name="superuser_home"),

]