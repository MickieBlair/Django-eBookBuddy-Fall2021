from django.urls import path

from reading_sessions.views import (
    student_landing_view,
    volunteer_landing_view,
    staff_landing_view,


    meeting_room_view,
    session_end_view,

    ajax_room_reset, 
    staff_reset_count,

    create_or_return_private_chat_ajax,
    ajax_id_new_chat,
    check_room_name,

    initial_entry_view,

    session_evaluation_view,
    link_session_evaluation_view,

    #testing
    testing_home_view,
    testing_staff_view,
    testing_student_view,
    testing_volunteer_view,

    #ajax jitsi apis
    by_jitsi_room_participants_ajax,
    get_rooms_and_participants,
    get_drop_for_user,


    #ajax help requests
    get_help_requests,
    create_help_request,
    ajax_help_mark_as_done,

    #ajax connection
    ajax_connection_status,

    #ajax profile
    ajax_get_user_profile,

    #ajax adjust
    adjust_user_status,

    ajax_check_room_mismatch,


    


)


app_name = 'reading_sessions'

urlpatterns = [
    path('volunteer_home/', volunteer_landing_view, name="volunteer_home"),
    path('student_home/', student_landing_view, name="student_home"),
    path('staff_home/', staff_landing_view, name="staff_home"),
    path('session_end/', session_end_view, name="session_end"),

    path('room/<room_slug>/', meeting_room_view, name="room"),

    path('ajax_room_reset_count/', ajax_room_reset, name="ajax_room_reset"),
    path('ajax_staff_reset_count/', staff_reset_count, name="staff_reset_count"),

    path('ajax_create_or_return_private_chat/', create_or_return_private_chat_ajax, name='create-or-return-private-chat'),
    path('ajax_id_new_chat/', ajax_id_new_chat, name='ajax_id_new_chat'),
    path('ajax_check_room_name/', check_room_name, name="ajax_check_name"),

    path('initial_entry/', initial_entry_view, name="initial_entry"),

    path('session_evaluation/', session_evaluation_view, name="session_evaluation"),
    path('session_evaluations/', link_session_evaluation_view, name="link_session_evaluation"),

    #api rooms
    path('ajax_by_room_participants/', by_jitsi_room_participants_ajax, name="ajax_by_room_participants"),
    path('ajax_get_room_participants/', get_rooms_and_participants, name="ajax_get_room_participants"),

    #ajax drops
    path('get_drop_for_user/', get_drop_for_user, name="get_drop_for_user"),

    # testing
    path('testing_home/', testing_home_view, name="testing_home"),
    path('testing_staff/<room_name>/', testing_staff_view, name="testing_staff"),
    path('testing_student/<room_name>/', testing_student_view, name="testing_student"),
    path('testing_volunteer/<room_name>/', testing_volunteer_view, name="testing_volunteer"),

    #ajax help requests
    path('get_help_requests/', get_help_requests, name="get_help_requests"),
    path('create_help_request/', create_help_request, name="create_help_request"),    
    path('ajax_help_mark_as_done/', ajax_help_mark_as_done, name="ajax_help_mark_as_done"),  

    #ajax ajax_connection_status
    path('ajax_connection_status/', ajax_connection_status, name="ajax_connection_status"),

    #ajax ajax_profile
    path('ajax_get_user_profile/', ajax_get_user_profile, name="ajax_get_user_profile"),

    #ajax ajax_profile
    path('adjust_user_status/', adjust_user_status, name="adjust_user_status"),
    path('ajax_check_room_mismatch/', ajax_check_room_mismatch, name="ajax_check_room_mismatch"),
 ]


     # initial_sessions_view,
    # session_lobby_room_view,
    # breakout_room_view,
    # pending_room_view,
    # 
    # # main_room_view,    
    # # unmatched_room_view,
    # room_left_view,
    # # clear_info,
    # # 
    # # volunteer_landing_view,
    # no_sessions_today_view,
    # ajax_load_jitsi_script,
    # # get_internet_speed,
    # staff_get_count,
    # staff_add_one,  
    # staff_reset_count,
    #  


    # # private_chat_room_view,
    # create_or_return_private_chat_ajax,
    # ajax_id_new_chat,

    # # Jitsi Calls
    # jitsi_joined_ajax,
    # jitsi_left_ajax,
    # jitsi_room_participants_count_ajax,

# )

    # # path('private/', private_chat_room_view, name='private-chat-room'),
    # # path('session-lobby/', main_room_view, name="main_room"),
    # # path('match-pending/', unmatched_room_view, name="pending"),
    # # path('clear_info/', clear_info, name="clear_info"),
    
    # # path('volunteers/', volunteer_landing_view, name="vol_landing"),
    
    
    # # path('<slug>/', breakout_room_view, name="breakout"),

    # # path('ajax/get_speed/', get_internet_speed, name="internet_speed"), 

    # path('initial_entry/', initial_sessions_view, name="initial_entry"),
    # path('room/session-lobby/', session_lobby_room_view, name="session_lobby"),
    # path('room/match-pending/', pending_room_view, name="pending"),
    # 
    # path('ajax_staff_get_count/', staff_get_count, name="staff_get_count"),
    # path('ajax_staff_add_one/', staff_add_one, name="staff_add_one"),
    # path('ajax_staff_reset_count/', staff_reset_count, name="staff_reset_count"),
    # 
    # 
    # path('after_meeting/', room_left_view, name="after_meeting"),
    # path('ajax_load_jitsi_script/', ajax_load_jitsi_script, name="ajax_load_jitsi"),
    # path('no_sessions/', no_sessions_today_view, name="no_sessions_today"),

    
    # path('ajax_create_or_return_private_chat/', create_or_return_private_chat_ajax, name='create-or-return-private-chat'),
    
    # path('room/<slug>/', breakout_room_view, name="breakout"),


    # path('ajax_jitsi_join/<room_id>/', jitsi_joined_ajax, name="jitsi_joined_ajax"),
    # path('ajax_jitsi_left/<room_id>/', jitsi_left_ajax, name="jitsi_left_ajax"),
    # path('jitsi_room_participants/', jitsi_room_participants_count_ajax, name="jitsi_room_participants"),
    
