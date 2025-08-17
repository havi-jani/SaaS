from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.urls import reverse
from helper import billing as bill
from django.contrib import messages
from subscription import utills as subs_utils
# Create your views here.

@login_required
def user_subscription_view(req):
    user_sub_obj, created = UserSubscription.objects.get_or_create(
        user = req.user
    )
    if req.method == 'POST':
        print('Refresh')
        finished = subs_utils.refresh_user_subscription(user_ids=[req.user.id], active_only=False)
        
        if finished:
            messages.success(req, "Your Plan details have been Refreshed")
        else:
            messages.error(req, "Your Plan details have not been Refreshed")
             
        return redirect(user_sub_obj.get_absolute_url())
    
    return render(req,"subscription/user_detail_view.html", {
        "subscription_data":user_sub_obj
    })

@login_required
def user_subscription_cancel_view(req):
    user_sub_obj, created = UserSubscription.objects.get_or_create(
        user = req.user
    )
    if req.method == 'POST':
        print('Refresh')
        if user_sub_obj.stripe_id and user_sub_obj.is_active_status:
                sub_data = bill.cancel_subscription(
                     user_sub_obj.stripe_id, 
                     reason="User wanted to End", 
                     feedback="other", 
                     cancel_at_period_end=True,
                     raw=False)
                
                for k , v in sub_data.items():
                     setattr(user_sub_obj, k, v)

                user_sub_obj.save()
        messages.success(req , "Your Plan has been cancelled")
        return redirect(user_sub_obj.get_absolute_url())
    
    return render(req,"subscription/user_cancel_view.html", {
        "subscription_data":user_sub_obj
    })

def subscription_price_view(req, interval="month"):
    qs = SubscriptionPrice.objects.filter(featured=True)

    interval_month = SubscriptionPrice.IntervalChoices.MONTHLY
    interval_year = SubscriptionPrice.IntervalChoices.YEARLY
    intervalList = qs.filter(
        interval=interval_month
    )    

    url_path = "Pricing_interval"

    monthPath = reverse(url_path, kwargs={"interval" : interval_month})
    yearPath = reverse(url_path, kwargs={"interval" : interval_year})
    active = interval_month

    if interval == interval_year:
        active= interval_year
        intervalList = qs.filter(
        interval=interval_year
        )
    
    return render(req, "subscription/pricing.html", {
        "interval" : intervalList,
        "monthPath" : monthPath,
        "yearPath" :  yearPath,
        "active": active,
        
    })