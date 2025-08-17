from typing import Any
from django.core.management.base import BaseCommand

from subscription  import utills as subs_utills

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        subs_utills.sync_subs_groups_permissions()

