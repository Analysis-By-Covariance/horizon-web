from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    name = "accounts"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import signals

        post_migrate.connect(signals.sync_groups_after_migrate, dispatch_uid="accounts.sync_groups")
