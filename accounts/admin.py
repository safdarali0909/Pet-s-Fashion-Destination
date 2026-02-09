from django.contrib import admin
from accounts.models import *
# Register your models here.

admin.site.register(Cart)
admin.site.register(Profile)
admin.site.register(CartItems)
admin.site.register(DeliveryAddress)
# admin.site.register(PaymentMethod)
admin.site.register(Order)
admin.site.register(Feedback)
admin.site.register(RazorpayPayment)
admin.site.register(MyUser)


