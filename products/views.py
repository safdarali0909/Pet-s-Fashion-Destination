from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import product
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from accounts.models import MyUser


def get_products(request, slug):
    product_obj = get_object_or_404(product, slug=slug)
    custom_user = None
    profile = None
    user_id = request.session.get('user_id')

    if user_id:
        try:
            custom_user = MyUser.objects.get(id=user_id)
            profile = custom_user.profile
        except MyUser.DoesNotExist:
            custom_user = None
        except profile.DoesNotExist:
            profile = None

    if product_obj.stock == 0:
        messages.warning(request, f"This product is currently out of stock.")
    elif product_obj.stock <= 5:  
        messages.warning(request, f"Only {product_obj.stock} item(s) left in stock!")
    

    context = {
        'product': product_obj,
        'custom_user': custom_user,
        'profile': profile,
        'available_stock': product_obj.stock,
        'delivery_date': timezone.now().date() + timedelta(days=7),
    }

    return render(request, 'products/product_detail.html', context)