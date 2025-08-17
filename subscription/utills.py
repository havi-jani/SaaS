
from helper import billing as bill
from django.db.models import Q
from subscription.models import *
from customers.models import Customers


def refresh_user_subscription(user_ids=None, active_only=True,days_left=0,days_ago = 0,day_start=0,day_end=0,verbose=False):

    qs = UserSubscription.objects.all()
    if active_only:
        qs = qs.by_active_trialing()
    if user_ids is not None:
        qs = qs.by_user_ids(user_ids=user_ids)
    
    if days_ago > 0 :
        qs = qs.by_days_ago(days_ago=days_ago)
    if days_left > 0 :
        qs = qs.by_days_left(days_left=days_left)
    if day_start > 0 and day_end > 0:
        qs = qs.by_range(days_start = day_start , days_end = day_end)


    complete_count = 0
    qs_count = qs.count()
    for obj in qs:
        if verbose:
            print(f"Updating User {obj.user} - {obj.subscription} - {obj.current_period_end}")
        if obj.stripe_id:
            sub_data = bill.get_subscription(obj.stripe_id , raw=False)
            for k , v in sub_data.items():
                setattr(obj, k, v)
            obj.save()

            complete_count += 1
    return complete_count == qs_count

def clear_dangling_subs():
    # print("Hello")
    qs = Customers.objects.filter(stripe_id__isnull = False)
    for customer_obj in qs:
        user = customer_obj.user
        customer_stripe_id =  customer_obj.stripe_id
        print(f"Sync the {user} - {customer_stripe_id} subs and remove old ones")
        subs = bill.get_customer_active_subscriptions(customer_stripe_id=customer_stripe_id)
        for sub in subs:
            existing_user_subs_qs = UserSubscription.objects.filter(stripe_id__iexact=F"{sub.id}".strip())
            if existing_user_subs_qs.exists():
                continue
            bill.cancel_subscription(sub.id, reason="Dandling active subscription", cancel_at_period_end=False)
            print(sub.id, existing_user_subs_qs.exists())
        

def sync_subs_groups_permissions():
            # print("Hello")
    qs = Subscription.objects.filter(active=True)
    for data in qs:
        # print(data.groups.all())
        sub_perms = data.permission.all()
        for grp in data.groups.all():
            grp.permissions.set(sub_perms)
            
        # print(data.permission.all())
