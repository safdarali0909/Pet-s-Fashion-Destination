from django.shortcuts import render,redirect,HttpResponseRedirect,HttpResponse
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from accounts.models import Cart,CartItems,Profile,DeliveryAddress,Order,Feedback,RazorpayPayment,MyUser
from products.models import *
from django.shortcuts import get_object_or_404
import logging
from django.utils.timezone import localtime
from django.utils import timezone
# import json
from django.contrib.auth.hashers import make_password,check_password
from itertools import groupby
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
import razorpay
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
logger = logging.getLogger(__name__)

# Create your views here.
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = MyUser.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id   # manually setting session
                return redirect('/')
            else:
                messages.warning(request, 'Invalid credentials')
        except MyUser.DoesNotExist:
            messages.warning(request, 'Invalid credentials')

        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first')
        email = request.POST.get('email')
        password = request.POST.get('pass')
        confirm_password = request.POST.get('confirm_password')

        user_obj = MyUser.objects.filter(email=email)

        if user_obj.exists():
            messages.warning(request, "Email already exists. Try another.")
            return HttpResponseRedirect(request.path_info)

        if not first_name or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return HttpResponseRedirect(request.path_info)

        if re.search(r'\d', first_name):
            messages.error(request, "Name should not contain numbers.")
            return HttpResponseRedirect(request.path_info)

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return HttpResponseRedirect(request.path_info)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return HttpResponseRedirect(request.path_info)

        email_username = email.split('@')[0]
        if email_username and email_username[0].isdigit():
            messages.error(request, "Email should not start with a number.")
            return HttpResponseRedirect(request.path_info)

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return HttpResponseRedirect(request.path_info)

        # Save new user
        hashed_password = make_password(password)
        new_user = MyUser.objects.create(
            email=email,
            username=first_name,
            password=hashed_password
        )

        # Create corresponding profile
        Profile.objects.create(
            user=new_user,
            name=first_name,
            email=email
        )

        messages.success(request, 'User registered successfully!')
        return redirect('Login')

    return render(request, 'accounts/register.html')


        
def add_to_cart(request, uid):
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

    
    product_obj = product.objects.get(uid=uid)
    user = custom_user
    cart_obj, _ = Cart.objects.get_or_create(user=user, is_paid=False)
    cart_item_obj, _ = CartItems.objects.get_or_create(cart=cart_obj, product=product_obj)
    
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
    else:
        
        quantity = int(request.GET.get('quantity', 1))

    
    if _ is False:  
        cart_item_obj.quantity += quantity
    else:  
        cart_item_obj.quantity = quantity
    
   
    cart = request.session.get('cart', {})
    
    if str(uid) in cart:
        cart[str(uid)] += quantity
    else:
        cart[str(uid)] = quantity

    request.session['cart'] = cart
    
  
    cart_item_obj.save()
    
    messages.success(request, f" item added to cart.")
   
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
   
def cart(request):
    custom_user = None
    profile = None
    user_id = request.session.get('user_id')

    if user_id:
        try:
            custom_user = MyUser.objects.get(id=user_id)
            profile = custom_user.profile  # Try to access profile
        except MyUser.DoesNotExist:
            custom_user = None
        except profile.DoesNotExist:
            profile = None

    cart_obj = Cart.objects.filter(is_paid=False, user=custom_user).first()
    cart_items = CartItems.objects.filter(cart=cart_obj)
    cart_total = sum(item.get_total_price() for item in cart_items)
    flat_rate_shipping = 0
    cart_total_plus_shipping = cart_total + flat_rate_shipping
    

    context = {
        'cartItems': cart_items,
        'cart': cart_obj,
        'cart_total': cart_total,
        'flat_rate_shipping': flat_rate_shipping,
        'cart_total_plus_shipping': cart_total_plus_shipping,
        'custom_user': custom_user,
        'profile': profile
    }
    return render(request, 'accounts/cart.html', context=context)
    




def remove_cart_item(request,uid):
    custom_user = None
    profile = None
    user_id = request.session.get('user_id')

    if user_id:
        try:
            custom_user = MyUser.objects.get(id=user_id)
            profile = custom_user.profile  # Try to access profile
        except MyUser.DoesNotExist:
            custom_user = None
        except profile.DoesNotExist:
            profile = None

    item = get_object_or_404(CartItems, uid=uid, cart__user=custom_user, cart__is_paid=False)
    item.delete()
    messages.error(request, 'Item removed from cart')
    return redirect('cart')
    








def userprofile(request):
   profile = Profile.objects.get(user=request.user)
    
   if request.method == 'POST':
        # Update profile fields
        profile.name = request.POST.get('name', profile.name)
        profile.title = request.POST.get('title', profile.title)
        profile.organization = request.POST.get('organization', profile.organization)
        profile.work_phone = request.POST.get('work_phone', profile.work_phone)
        profile.mobile_phone = request.POST.get('mobile_phone', profile.mobile_phone)
        profile.email = request.POST.get('email', profile.email)
        
        # Handle file upload
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
        
        profile.save()
        return redirect('/')
    
   return render(request, 'accounts/userprofile.html', {'profile': profile})


def shop(request):
    custom_user = None
    profile = None
    user_id = request.session.get('user_id')

    if user_id:
        try:
            custom_user = MyUser.objects.get(id=user_id)
            profile = custom_user.profile
        except MyUser.DoesNotExist:
            custom_user = None
        except Exception:
            profile = None

    # === Filter Parameters ===
    category_filter = request.GET.get("category", "").strip()
    price_filters = request.GET.getlist("price")  # ✅ checkbox allows multiple values
    # print("Selected category:", category_filter)
    # print("Selected price filters:", price_filters)

    # === Base QuerySet ===
    all_products = product.objects.select_related('category').all()

    # === Apply Category Filter ===
    if category_filter:
        all_products = all_products.filter(category__category_name=category_filter)

    # === Apply Multiple Price Filters ===
    if price_filters:
        price_query = Q()
        for price_range in price_filters:
            price_range = price_range.strip().replace("–", "-")  # Normalize em dash
            if price_range == "0-500":
                price_query |= Q(price__gte=0, price__lte=500)
            elif price_range == "500-1000":
                price_query |= Q(price__gte=500, price__lte=1000)
            elif price_range == "1000-5000":
                price_query |= Q(price__gte=1000, price__lte=5000)
            elif price_range == "5000":
                price_query |= Q(price__gt=5000)
        all_products = all_products.filter(price_query)

    print("Price filter applied. SQL:", all_products.query)

    # === Group Products by Category for Display ===
    all_products = all_products.order_by('category_id')
    grouped_products = {
        cat: list(items)
        for cat, items in groupby(all_products, key=lambda x: x.category)
    }

    # === Price filter options (for template checkboxes)
    price_choices = [
        ("0-500", "Under ₹500"),
        ("500-1000", "₹500 - ₹1000"),
        ("1000-5000", "₹1000 - ₹5000"),
        ("5000", "Above ₹5000"),
    ]

    # === Dropdown Data for Filters ===
    all_categories = category.objects.values_list("category_name", flat=True).distinct()
    categories = category.objects.all()

    # === Context ===
    context = {
        'custom_user': custom_user,
        'profile': profile,
        'products': all_products,
        'grouped_products': grouped_products,
        'categories': categories,
        'all_categories': all_categories,
        'selected_category': category_filter,
        'selected_prices': price_filters,     # ✅ to pre-check checkboxes
        'price_choices': price_choices        # ✅ to render checkbox list
    }

    return render(request, 'accounts/shop.html', context)
def checkout_view1(request):
    custom_user = None
    profile = None
    user_id = request.session.get('user_id')

    if user_id:
        try:
            custom_user = MyUser.objects.get(id=user_id)
            profile = custom_user.profile  # Try to access profile
        except MyUser.DoesNotExist:
            custom_user = None
        except profile.DoesNotExist:
            profile = None
    user = custom_user

    cart = Cart.objects.filter(is_paid=False, user=user).first()
    cart_items = CartItems.objects.filter(cart=cart)
    cart_total = sum(item.get_total_price() for item in cart_items)
    delivery_address = DeliveryAddress.objects.filter(user=user).first()
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({
            'amount': int(cart_total * 100),  # amount in paisa
            'currency': 'INR',
            'payment_capture': 1
    })
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_signature = request.POST.get('razorpay_signature')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            # Verify signature
            client.utility.verify_payment_signature(params_dict)

            # Save payment record
            RazorpayPayment.objects.create(
                user=user,
                order_id=razorpay_order_id,
                payment_id=razorpay_payment_id,
                signature=razorpay_signature,
                amount=cart_total,
                currency='INR',
                status='paid'
            )

            # Save order and clear cart
            for item in cart_items:
                product = item.product

                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save()

                    Order.objects.create(
                        user=user,
                        product=product,
                        quantity=item.quantity,
                        order_date=timezone.now(),
                        status='Order Placed',
                        delivery_address=delivery_address,
                        total_price=item.get_total_price()
                    )
                else:
                    return JsonResponse({'error': f"Not enough stock for {product.title}. Only {product.stock} left."}, status=400)

            cart.is_paid = True
            cart.save()
            cart_items.delete()

            return JsonResponse({'message': 'Payment verified and order placed successfully'})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'error': 'Signature verification failed'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)  
    print("************")
    print(payment)
    print("************")
    context = {
        'cartItems': cart_items,
        'cart': cart,
        'cart_total': cart_total,
        'delivery_address': delivery_address,
        'payment': payment,
        'custom_user': custom_user,
        'profile': profile
    }

    return render(request, 'accounts/checkout.html', context)

def delivery_address(request):
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
    if request.method == "POST":

        user = custom_user
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        Mono = request.POST.get('MoNo')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip')

        delivery_address = DeliveryAddress.objects.create(
            user=user,
            name=name,
            email=email,
            address=address,
            city=city,
            zip_code=zip_code,
            contact_number=Mono
    )
        delivery_address.save()
        messages.success(request, 'Delivery Address Saved')
        return redirect('checkout')
    context={
        'custom_user': custom_user,
        'profile': profile
    }
    return render(request, 'accounts/add_address.html',context)
  


def order(request):
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
    orders = Order.objects.filter(user=custom_user)

    context ={
        'orders': orders,
        'custom_user': custom_user,
        'profile': profile
    }
    return render(request, 'accounts/order.html',context)
def cancel_order_view(request, order_id):
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

    order = get_object_or_404(Order, id=order_id, user=custom_user)

    if order.status != 'Cancelled':
        # Update product stock
        try:
            prod = order.product  
            prod.stock += order.quantity  
            prod.save()
        except Exception as e:
            print("Error updating stock:", e)
            messages.error(request, "Something went wrong while updating stock.")

        # Then cancel the order
        order.status = 'Cancelled'
        order.save()
        messages.error(request, "Order has been cancelled and stock updated.")
    else:
        messages.warning(request, "Order was already cancelled.")

    return redirect('order')
def feedback_view(request):
    custom_user = None
    profile = None
    user_id = request.session.get('user_id')

    if user_id:
        try:
            custom_user = MyUser.objects.get(id=user_id)
            profile = custom_user.profile  # Try to access profile
        except MyUser.DoesNotExist:
            custom_user = None
        except profile.DoesNotExist:
            profile = None
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Optionally save to database if Feedback model exists
        Feedback.objects.create(name=name, email=email, message=message)

        messages.success(request, "Thanks for your feedback!")
        return redirect('feedback')
    
    # user = User.objects.get(username=request.user)
    context={
        'custom_user': custom_user,
        'profile': profile
    }

    return render(request, 'accounts/feedback.html',context)

def update_cart_item_quantity(request, uid):
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

    if request.method == 'POST':
        item = get_object_or_404(CartItems, uid=uid, cart__user=custom_user, cart__is_paid=False)
        product = item.product  # Assuming CartItems has a ForeignKey to Product
        action = request.POST.get('action')

        if action == 'increase':
            if item.quantity < product.stock:
                item.quantity += 1
                item.save()
                messages.success(request, 'Quantity increased.')
            else:
                messages.warning(request, f"Only {product.stock} item(s) in stock.")
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
                messages.success(request, 'Quantity decreased.')
            else:
                item.delete()
                messages.success(request, 'Item removed from cart.')
        else:
            messages.error(request, 'Invalid action.')

    return redirect('cart')


 # For GET requests, redirect elsewhere
def logout_view(request):
    logout(request)
    return redirect("Login")

def userprofile(request):
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
    profile = Profile.objects.get(user=user_id)

    if request.method == 'POST':
        # Update profile fields
        profile.name = request.POST.get('name', profile.name)
        profile.email = request.POST.get('email', profile.email)

        # Handle file upload
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        # return redirect('/')

    return render(request, 'accounts/userprofile.html', {'profile': profile})