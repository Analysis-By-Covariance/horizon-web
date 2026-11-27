from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings

from accounts.mixins import OwnerOrPermissionRequiredMixin
from accounts.permissions import ADMIN, GROUP_PERMISSIONS, MODERATOR, can_access

User = get_user_model()


def fake_obj(owner_id):
    # Stands in for an OwnedModel instance; uses an existing model's perms.
    return SimpleNamespace(owner_id=owner_id, _meta=SimpleNamespace(app_label="accounts", model_name="user"))


class SyncGroupsTests(TestCase):
    def test_groups_exist_after_migrate_and_command_is_idempotent(self):
        call_command("sync_groups", verbosity=0)
        call_command("sync_groups", verbosity=0)
        self.assertEqual(Group.objects.filter(name__in=GROUP_PERMISSIONS).count(), len(GROUP_PERMISSIONS))
        self.assertEqual(Group.objects.get(name=ADMIN).permissions.count(), Permission.objects.count())


class CanAccessTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", "o@example.com", "x")
        self.other = User.objects.create_user("other", "x@example.com", "x")
        self.mod = User.objects.create_user("mod", "m@example.com", "x")
        group = Group.objects.get_or_create(name=MODERATOR)[0]
        group.permissions.add(Permission.objects.get(content_type__app_label="accounts", codename="change_user"))
        self.mod.groups.add(group)
        self.obj = fake_obj(self.owner.pk)

    def test_owner_allowed(self):
        self.assertTrue(can_access(self.owner, self.obj))

    def test_other_member_denied(self):
        self.assertFalse(can_access(self.other, self.obj))

    def test_permission_holder_allowed(self):
        self.assertTrue(can_access(self.mod, self.obj))
        self.assertFalse(can_access(self.mod, self.obj, "delete"))

    def test_mixin_raises_for_non_owner(self):
        class Base:
            def get_object(self, queryset=None):
                return fake_obj(owner_id=-1)

        class View(OwnerOrPermissionRequiredMixin, Base):
            pass

        view = View()
        view.request = RequestFactory().get("/")
        view.request.user = self.other
        with self.assertRaises(PermissionDenied):
            view.get_object()


@override_settings(ROOT_URLCONF="accounts.tests.urls")
class HtmxAuthMiddlewareTests(TestCase):
    def test_anonymous_htmx_gets_hx_redirect_to_login(self):
        resp = self.client.get("/protected/", headers={"HX-Request": "true"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("/accounts/login/", resp["HX-Redirect"])

    def test_anonymous_plain_request_gets_normal_redirect(self):
        resp = self.client.get("/protected/")
        self.assertEqual(resp.status_code, 302)

    def test_forbidden_htmx_gets_partial(self):
        resp = self.client.get("/forbidden/", headers={"HX-Request": "true"})
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp["HX-Retarget"], "#messages")
        self.assertContains(resp, "permission", status_code=403)
