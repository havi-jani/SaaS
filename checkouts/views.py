from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from subscription.models import SubscriptionPrice, Subscription,UserSubscription
from helper import billing as bill
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest
from django.contrib import messages
# Create your views here.

User = get_user_model()
BASE_URL = settings.BASE_URL

def product_price_redirect_view(req ,price_id=None, *args, **kwargs):
    req.session['checkout_subscription_price_id'] = price_id
    return redirect("checkout_start")


@login_required
def checkout_redirect_view(req):
    checkout_subscription_price_id = req.session.get('checkout_subscription_price_id')
    try:
        obj = SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except:
        obj = None


    if checkout_subscription_price_id is None or obj is None:
        return redirect("Pricing")
    customer_stripe_id = req.user.customers.stripe_id
    # print(dir(req.user))
    # print(customer_stripe_id)

    success_url_path = reverse("checkout_end")
    pricing_url_path = reverse("Pricing")
    success_url = f"{BASE_URL}{success_url_path}"
    cancel_url = f"{BASE_URL}{pricing_url_path}"
    price_stripe_id = obj.stripe_id

    url = bill.start_checkout_session(
        customer_stripe_id,
        success_url=success_url,
        cancel_url=cancel_url,
        price_stripe_id=price_stripe_id,
        raw=False,
    )

    return redirect(url)

def checkout_finalize_view(req):
   
    session_id = req.GET.get('session_id')
    checkout_data = bill.get_checkout_customer_plan(session_id) 
    plan_id = checkout_data.pop('plan_id')
    customer_id = checkout_data.pop('customer_id')
    sub_stripe_id = checkout_data.pop('sub_stripe_id')
    subscription_data = {**checkout_data}

    try:
        sub_obj = Subscription.objects.get(subscriptionprice__stripe_id=plan_id)
    except:
        sub_obj = None
    try:
        user_obj = User.objects.get(customers__stripe_id = customer_id)
    except:
        user_obj = None


    _user_sub_exists = False
    updateed_sub_option = {
        "subscription": sub_obj,
        "stripe_id": sub_stripe_id,
        "user_cancelled": False,
        **subscription_data,
    }
    try:
        _user_sub_obj = UserSubscription.objects.get(user=user_obj)
        _user_sub_exists = True
    except UserSubscription.DoesNotExist:
        _user_sub_obj = UserSubscription.objects.create(user=user_obj, **updateed_sub_option )
    except:
        _user_sub_obj = None

    if None in [sub_obj, user_obj, _user_sub_obj]:
        return HttpResponseBadRequest("There was an error with Your Account , please contact us...!")

    if _user_sub_exists:

        # Cancel old sub 
        old_stripe_id = _user_sub_obj.stripe_id
        same_stripe_id = sub_stripe_id == old_stripe_id
        if old_stripe_id is not None and not same_stripe_id:
            try:    
                bill.cancel_subscription(stripe_id=old_stripe_id, reason="Auto ended, New Membership", feedback="other")
            except:
                pass
        # assign new sub
        for k,v in updateed_sub_option.items():
            setattr(_user_sub_obj, k, v)
        _user_sub_obj.save()
        messages.success(req , "Success ! Thank You for Joining with US..")
        return redirect(_user_sub_obj.get_absolute_url())

    context = {
        "data": 1,
    }
    return render(req, "checkout/success.html", context )
