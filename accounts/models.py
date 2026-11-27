from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _


class UserManager(DjangoUserManager):
    @classmethod
    def normalize_email(cls, email):
        # Django only lower-cases the domain; we treat the whole address as
        # case-insensitive so "Bob@x.com" and "bob@x.com" are one account.
        return (email or "").strip().lower()

    def get_by_natural_key(self, username):
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username})


class User(AbstractUser):
    """Project user. Log in with either username or email (see allauth settings)."""

    email = models.EmailField(_("email address"), unique=True)
    display_name = models.CharField(_("display name"), max_length=150, blank=True)
    avatar_url = models.URLField(_("avatar URL"), blank=True)

    objects = UserManager()

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_user_email_ci_unique"),
            models.UniqueConstraint(Lower("username"), name="accounts_user_username_ci_unique"),
        ]

    def save(self, *args, **kwargs):
        self.email = UserManager.normalize_email(self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name or self.username


class OwnedModel(models.Model):
    """Abstract base for domain models that belong to a user.

    Pair with `accounts.permissions.can_access` / `OwnerOrPermissionRequiredMixin`.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
    )

    class Meta:
        abstract = True
