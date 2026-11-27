from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from accounts.adapters import SocialAccountAdapter

User = get_user_model()


class SocialAdapterTests(TestCase):
    def test_populate_user_fills_display_name_and_avatar(self):
        sociallogin = MagicMock()
        sociallogin.user = User()
        sociallogin.account.get_avatar_url.return_value = "https://img.example.com/a.png"
        request = RequestFactory().get("/")
        user = SocialAccountAdapter(request).populate_user(
            request, sociallogin, {"email": "Ada@Example.com", "first_name": "Ada", "last_name": "Lovelace"}
        )
        self.assertEqual(user.display_name, "Ada Lovelace")
        self.assertEqual(user.avatar_url, "https://img.example.com/a.png")
