"""Authorization: default groups, their permissions, and object-level checks."""

import logging

from django.contrib.auth.models import Group, Permission

logger = logging.getLogger(__name__)

MEMBER = "Member"
MODERATOR = "Moderator"
ADMIN = "Admin"
DEFAULT_GROUP = MEMBER

ALL = "__all__"

# Single source of truth for group permissions, as "app_label.codename".
# Add entries here as domain models are created, then run `manage.py sync_groups`
# (it also runs automatically after every `migrate`).
#
# Convention: Members get view/add (and change/delete *their own* objects via
# ownership checks, not via these perms). Moderators get change/delete on
# everyone's content. Admin gets every permission.
GROUP_PERMISSIONS = {
    MEMBER: [
        # e.g. "posts.view_post", "posts.add_post",
    ],
    MODERATOR: [
        # e.g. "posts.view_post", "posts.add_post", "posts.change_post", "posts.delete_post",
    ],
    ADMIN: ALL,
}


def sync_groups(verbosity=1):
    """Create the default groups and set their permissions. Idempotent."""
    for name, perms in GROUP_PERMISSIONS.items():
        group, created = Group.objects.get_or_create(name=name)
        if perms == ALL:
            wanted = list(Permission.objects.all())
        else:
            wanted = []
            for dotted in perms:
                app_label, codename = dotted.split(".", 1)
                perm = Permission.objects.filter(
                    content_type__app_label=app_label, codename=codename
                ).first()
                if perm is None:
                    logger.warning("sync_groups: permission %s does not exist (yet)", dotted)
                    continue
                wanted.append(perm)
        group.permissions.set(wanted)
        if verbosity:
            logger.info("%s group %s (%d perms)", "Created" if created else "Updated", name, len(wanted))


def perm_name(obj, action):
    """'change' + Post instance -> 'posts.change_post'."""
    meta = obj._meta
    return f"{meta.app_label}.{action}_{meta.model_name}"


def can_access(user, obj, action="change"):
    """Owner of `obj`, or holder of the model-level permission for `action`."""
    if not user.is_authenticated or not user.is_active:
        return False
    if user.has_perm(perm_name(obj, action)):
        return True
    return getattr(obj, "owner_id", None) == user.pk
