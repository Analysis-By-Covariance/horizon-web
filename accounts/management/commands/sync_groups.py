from django.core.management.base import BaseCommand

from accounts.permissions import GROUP_PERMISSIONS, sync_groups


class Command(BaseCommand):
    help = "Create default groups (Member, Moderator, Admin) and apply GROUP_PERMISSIONS."

    def handle(self, *args, **options):
        sync_groups(verbosity=options["verbosity"])
        self.stdout.write(self.style.SUCCESS(f"Synced groups: {', '.join(GROUP_PERMISSIONS)}"))
