from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from accounts.permissions import MEMBER

User = get_user_model()
PASSWORD = "a-Strong-pass-123"


class UserModelTests(TestCase):
    def test_email_is_normalized_to_lowercase(self):
        user = User.objects.create_user("bob", "Bob@Example.COM", PASSWORD)
        self.assertEqual(user.email, "bob@example.com")

    def test_email_unique_case_insensitive(self):
        User.objects.create_user("bob", "bob@example.com", PASSWORD)
        with self.assertRaises(IntegrityError):
            User.objects.create_user("bobby", "BOB@example.com", PASSWORD)

    def test_username_unique_case_insensitive(self):
        User.objects.create_user("bob", "bob@example.com", PASSWORD)
        with self.assertRaises(IntegrityError):
            User.objects.create_user("BOB", "other@example.com", PASSWORD)


class SignupLoginTests(TestCase):
    def test_signup_adds_member_group(self):
        resp = self.client.post(reverse("account_signup"), {
            "email": "new@example.com", "username": "newbie",
            "password1": PASSWORD, "password2": PASSWORD,
        })
        self.assertEqual(resp.status_code, 302)
        user = User.objects.get(username="newbie")
        self.assertTrue(user.groups.filter(name=MEMBER).exists())

    def test_signup_rejects_duplicate_email_any_case(self):
        User.objects.create_user("bob", "bob@example.com", PASSWORD)
        resp = self.client.post(reverse("account_signup"), {
            "email": "BOB@example.com", "username": "bob2",
            "password1": PASSWORD, "password2": PASSWORD,
        })
        self.assertEqual(resp.status_code, 200)  # form re-rendered with error
        self.assertFalse(User.objects.filter(username="bob2").exists())

    def _login(self, login):
        return self.client.post(reverse("account_login"), {"login": login, "password": PASSWORD})

    def test_login_with_email(self):
        User.objects.create_user("bob", "bob@example.com", PASSWORD)
        self.assertEqual(self._login("bob@example.com").status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_username(self):
        User.objects.create_user("bob", "bob@example.com", PASSWORD)
        self.assertEqual(self._login("bob").status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_wrong_password(self):
        User.objects.create_user("bob", "bob@example.com", PASSWORD)
        resp = self.client.post(reverse("account_login"), {"login": "bob", "password": "nope"})
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
