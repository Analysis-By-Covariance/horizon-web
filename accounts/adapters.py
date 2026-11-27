from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """Hook point for signup/login behaviour.

    Default-group assignment lives in `accounts.signals` (it must also cover
    social signups). HTMX redirects are handled by `HtmxAuthMiddleware`.
    """


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        # allauth fills username/email and generates a unique username if needed.
        user = super().populate_user(request, sociallogin, data)
        if not user.display_name:
            full = " ".join(filter(None, [data.get("first_name"), data.get("last_name")]))
            user.display_name = (data.get("name") or full or "")[:150]
        if not user.avatar_url:
            user.avatar_url = sociallogin.account.get_avatar_url() or ""
        return user
