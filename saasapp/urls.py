from django.urls import path , include
from .views import *
from auth import views as auth
from subscription import views as subs
from checkouts import views as check



urlpatterns = [
    path('', homepage , name='Home'),
    # path('login/', auth.loginView),
    path('accounts/',include('allauth.urls')),
    # path('register/', auth.registerView),
    path('accounts/billing/',subs.user_subscription_view, name="Subscription_Details"),
    path('accounts/billing/cancel/',subs.user_subscription_cancel_view, name="Subscription_Cancel"),
    path('profiles/',include('profiles.urls')),
    path('pricing/', subs.subscription_price_view, name="Pricing"),
    path('pricing/<str:interval>', subs.subscription_price_view, name="Pricing_interval"),
    path('checkout/sub-price/<int:price_id>/', check.product_price_redirect_view, name="Sub_price_checkout"),
    path('checkout/start/', check.checkout_redirect_view, name="checkout_start"),
    path('checkout/success/', check.checkout_finalize_view, name="checkout_end"),



]
