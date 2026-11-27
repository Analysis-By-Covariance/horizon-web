from django import template

from accounts.permissions import can_access

register = template.Library()


@register.filter
def can_edit(user, obj):
    """{% if request.user|can_edit:post %}…{% endif %}"""
    return can_access(user, obj, "change")


@register.filter
def can_delete(user, obj):
    return can_access(user, obj, "delete")


@register.filter
def in_group(user, name):
    """{% if request.user|in_group:"Moderator" %}…{% endif %}"""
    return user.is_authenticated and user.groups.filter(name=name).exists()
