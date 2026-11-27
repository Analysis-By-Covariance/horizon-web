from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django_htmx.http import HttpResponseClientRedirect

REDIRECT_CODES = {301, 302, 303, 307, 308}


class HtmxAuthMiddleware:
    """Make auth outcomes behave for HTMX requests.

    - Redirects (e.g. login_required -> login page, login success -> next)
      become `HX-Redirect`, so the browser navigates instead of HTMX swapping
      a whole page into a fragment target.
    - PermissionDenied becomes a small 403 partial retargeted to #messages.

    Requires django_htmx.middleware.HtmxMiddleware earlier in MIDDLEWARE.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            getattr(request, "htmx", False)
            and response.status_code in REDIRECT_CODES
            and response.has_header("Location")
        ):
            return HttpResponseClientRedirect(response["Location"])
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied) and getattr(request, "htmx", False):
            response = render(request, "partials/forbidden.html", status=403)
            response["HX-Retarget"] = "#messages"
            response["HX-Reswap"] = "innerHTML"
            return response
        return None
