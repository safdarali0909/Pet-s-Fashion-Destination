from django.contrib import admin
from products.models import *


admin.site.register(category)
# admin.site.register(coupon)


class ProductImageAdmin(admin.StackedInline):
    model = productsImage

class ProductAdmin(admin.ModelAdmin):
    list_display =['product_name','price']
    inlines = [ProductImageAdmin]


admin.site.register(product,ProductAdmin)
admin.site.register(productsImage)