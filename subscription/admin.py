from django.contrib import admin
from .models import *

# Register your models here.
class SubscriptionAdminPrice(admin.TabularInline):
    model = SubscriptionPrice
    readonly_fields = ['stripe_id']
    extra = 0
    # can_delete = False
    

class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionAdminPrice]
    list_display=  ['name', 'active']
    readonly_fields = ['stripe_id']


admin.site.register(Subscription, SubscriptionAdmin)

admin.site.register(UserSubscription)
