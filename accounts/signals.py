from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group
from django.dispatch import receiver

from .permissions import DEFAULT_GROUP, sync_groups


@receiver(user_signed_up)
def add_to_default_group(sender, request, user, **kwargs):
    """Every new account (password or social signup) starts as a Member."""
    group, _ = Group.objects.get_or_create(name=DEFAULT_GROUP)
    user.groups.add(group)


def sync_groups_after_migrate(sender, **kwargs):
    # Runs after each app migrates, so permissions for newly added models are
    # picked up. Cheap and idempotent.
    sync_groups(verbosity=0)
