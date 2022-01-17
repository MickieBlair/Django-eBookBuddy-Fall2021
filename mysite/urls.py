"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url

from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView


from pages.views import(
    home_screen_view,
    pending_approval_view,
    updating_in_progress_view,

)

from users.views import(
    login_view,
    logout_view,
    # registration_view,
    must_authenticate_view,
    denied_view,
    login_as_different_user,
    email_check,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),),
    
    path('', home_screen_view, name="home"),
    path('pending_approval/', pending_approval_view, name="pending_approval"),
    path('update_in_progress/', updating_in_progress_view, name="update_in_progress"),
    
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('must_authenticate/', must_authenticate_view, name="must_authenticate"),
    path('access_denied/', denied_view, name="access_denied"),
    path('change_user/', login_as_different_user, name="change_user"),


    path('site_admin/', include('site_admin.urls', 'site_admin')),
    path('sessions/', include('reading_sessions.urls', 'reading_sessions')),
    path('testing/', include('testing.urls', 'testing')),

    

    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), 
        name='password_change'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), 
        name='password_change_done'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
     name='password_reset_complete'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
        name='password_reset_confirm'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'),
     name='password_reset_done'), 

    path('email_check/', email_check, name="email_check"),
]


handler404 = 'mysite.views.custom_page_not_found_view'
handler500 = 'mysite.views.custom_error_view'
handler403 = 'mysite.views.custom_permission_denied_view'
handler400 = 'mysite.views.custom_bad_request_view'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



