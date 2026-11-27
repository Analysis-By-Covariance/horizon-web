from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .permissions import can_access


class OwnerOrPermissionRequiredMixin(LoginRequiredMixin):
    """For SingleObjectMixin views (Detail/Update/DeleteView).

    Allows the object's owner, or anyone with `<app>.<permission_action>_<model>`.
    Anonymous users are redirected to login; others get 403 (an HTMX partial
    for HTMX requests, via HtmxAuthMiddleware).
    """

    permission_action = "change"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not can_access(self.request.user, obj, self.permission_action):
            raise PermissionDenied
        return obj
