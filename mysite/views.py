from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponseServerError
from django.conf import settings

from django.core.mail import send_mail



# def custom_page_not_found_view(request, exception):
#     print("handler404")
#     return render(request, "404.html", {})

# def custom_error_view(request, exception=None):
#     return render(request, "500.html", {})

def custom_permission_denied_view(request, exception=None):
    return render(request, 'users/access_denied.html', {})

def custom_bad_request_view(request, exception=None):
    return render(request, "500.html", {})


def custom_error_view(request):
    print("handler500")
    t = get_template('500.html')
    response = HttpResponseServerError(t.render())
    response.status_code = 500
    # from_user = str(settings.SERVER_EMAIL)
    # to_user = 'contact@mickieblair.com'
    # print(from_user, to_user)
    # send_mail(
    #     'handler500',
    #     'custom_error_view',
    #     from_user,
    #     [to_user,],
    #     fail_silently=False,
    #     )
    return response


def custom_page_not_found_view(request, exception):
    print("handler404")
    t = get_template('404.html')
    response = HttpResponseServerError(t.render())
    response.status_code = 404

    # from_user = str(settings.SERVER_EMAIL)
    # to_user = 'contact@mickieblair.com'
    # full_url = request.build_absolute_uri()
    # print(from_user, to_user)
    # send_mail(
    #     'handler404',
    #     full_url,
    #     from_user,
    #     [to_user,],
    #     fail_silently=False,
    #     )
    return response