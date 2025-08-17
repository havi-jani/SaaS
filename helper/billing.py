import stripe
from decouple import config
from . import date_utils
DJANGO_DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
STRIPE_SECRETE_KEY = config("STRIPE_SECRETE_KEY", default="", cast=str)


if "sk_test" in STRIPE_SECRETE_KEY and not DJANGO_DEBUG:
    raise ValueError("Invalid Sceret Key")

stripe.api_key = STRIPE_SECRETE_KEY


def serialize_subscription_data(subscription_response):
  status = subscription_response.status
  item = subscription_response["items"]["data"][0]
  current_period_start = date_utils.timestamp_as_datetime(item["current_period_start"])
  current_period_end =date_utils.timestamp_as_datetime(item["current_period_end"])
  cancel_at_period_end = subscription_response.cancel_at_period_end

  data = {
      "current_period_start": current_period_start,
      "current_period_end": current_period_end,
      "status":status,
      "cancel_at_period_end":cancel_at_period_end,
  }
  return data

def create_customer(name="", email="",metadata={},raw=False):
  customer = stripe.Customer.create(
    name=name,
    email=email,
    metadata=metadata,
  )
  if raw:
     return customer
  stripe_id = customer.id
  return stripe_id

def create_product(name="",metadata={},raw=False):
  customer = stripe.Product.create(
    name=name,
    metadata=metadata,
  )
  if raw:
     return customer
  stripe_id = customer.id
  return stripe_id

def create_price(currency="",unit_amount="",interval="",product=None, metadata={}, raw=False):

  if product is None:
     return None
  
  price = stripe.Price.create(
    currency=currency,
    unit_amount=unit_amount,
    recurring={"interval" : interval},
    product=product,
    metadata=metadata,
  )

  if raw:
     return price
  stripe_id = price.id
  return stripe_id


def start_checkout_session(customer_id,success_url="",cancel_url="",price_stripe_id="",raw=True):

  if not success_url.endswith("?session_id={CHECKOUT_SESSION_ID}"):
     success_url = f"{success_url}" + "?session_id={CHECKOUT_SESSION_ID}"
  session = stripe.checkout.Session.create(
  customer=customer_id,
  success_url=success_url,
  cancel_url=cancel_url,
  line_items=[{"price": price_stripe_id, "quantity": 1}],
  mode="subscription",
  )
  if raw:
     return session
  return session.url

def get_checkout_session(stripe_id, raw=False):
    
    session = stripe.checkout.Session.retrieve(
          stripe_id,
      )
    
    if raw:
      return session
    return session.url

def get_subscription(stripe_id, raw=True):
    
    session = stripe.Subscription.retrieve(
          stripe_id,
      )
    
    if raw:
      return session
    return serialize_subscription_data(session)

def get_checkout_customer_plan(session_id,):
   checkout_res = get_checkout_session(
       session_id,
       raw=True,
   )
   customer_id = checkout_res.customer
   sub_stripe_id = checkout_res.subscription
   sub_res = get_subscription(
       sub_stripe_id,
       raw=True,
   )
   sub_plan = sub_res.plan
   subscription_data = serialize_subscription_data(sub_res)

   

   data = {
      "customer_id":customer_id,
      "plan_id": sub_plan.id,
      "sub_stripe_id":sub_stripe_id,
      **subscription_data

   }
   return data

def get_customer_active_subscriptions(customer_stripe_id):
    
    session = stripe.Subscription.list(
          customer=customer_stripe_id,
          status="active",
      )
    
    return session



def cancel_subscription(stripe_id,reason="",feedback="other", cancel_at_period_end =False, raw=True):
    
    if cancel_at_period_end:
      session = stripe.Subscription.modify(
            stripe_id,
            cancel_at_period_end=cancel_at_period_end,
            cancellation_details={"comment" : reason,
                                  "feedback": feedback}
        )
    else:
      session = stripe.Subscription.cancel(
            stripe_id,
            cancellation_details={"comment" : reason,
                                  "feedback": feedback}
        )
    if raw:
      return session
    return serialize_subscription_data(session)