from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import ProfileForm


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_template_names(self):
        if self.request.htmx and not self.request.htmx.boosted:
            return ["accounts/partials/profile_form.html"]
        return [self.template_name]

    def form_valid(self, form):
        messages.success(self.request, "Profile updated.")
        return super().form_valid(form)
