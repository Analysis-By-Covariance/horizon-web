from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.urls import include, path


@login_required
def protected(request):
    return HttpResponse("ok")


def forbidden(request):
    raise PermissionDenied


urlpatterns = [
    path("protected/", protected),
    path("forbidden/", forbidden),
    path("accounts/", include("allauth.urls")),
]
