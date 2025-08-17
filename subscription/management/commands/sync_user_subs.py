from typing import Any
from django.core.management.base import BaseCommand
from helper import billing as bill

from subscription import utills as subs_utills
from customers.models import Customers
class Command(BaseCommand):

    def add_arguments(self, parser):
        
        parser.add_argument("--day-start", default=0,type=int)
        parser.add_argument("--day-end", default=0,type=int)
        parser.add_argument("--days-left", default=0,type=int)
        parser.add_argument("--days-ago", default=0,type=int)
        parser.add_argument("--clear-dangling", action="store_true", default=False)
        # return super().add_arguments(parser)


    def handle(self, *args: Any, **options: Any):
        days_left = options.get("days_left")
        days_ago = options.get("days_ago")
        day_start = options.get("day_start")
        day_end = options.get("day_end")
        clear_dangling = options.get("clear_dangling")
        if clear_dangling:
            print("Clearing dangling not in use active subs")
            subs_utills.clear_dangling_subs()
        else:
            print("Sync active subs")
            done = subs_utills.refresh_user_subscription(
                active_only=True, 
                days_left=days_left, 
                days_ago=days_ago,
                day_start=day_start,
                day_end=day_end,
                verbose=True)
            if done:
                print("Done")
