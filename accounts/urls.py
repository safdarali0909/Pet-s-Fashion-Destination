from django.urls import path
from accounts import views


urlpatterns = [
   
   path('shop',views.shop,name="shop"),
   path("register",views.register_view,name="Register"),
   path("login",views.user_login,name="Login"),
   path("cart/",views.cart,name="cart"),  
   # path("activate/<email_token>",views.activate_email, name="activate"),
   path("add-to-cart/<uid>/",views.add_to_cart,name="add_to_cart"),
   path("remove-cart-items/<uid>/",views.remove_cart_item, name="remove_cart_item"),
   path('update-quantity/<uid>/',views.update_cart_item_quantity, name='update_cart_item_quantity'),
   path("checkout/",views.checkout_view1, name="checkout"),
   # path('place_order/',views.place_order_view, name='place_order'),
   path('order_details/',views.order, name='order'),
   path('logout/',views.logout_view, name='logout'),
   path('add_address/',views.delivery_address, name='add_address'),
   path('cancel-order/<int:order_id>/', views.cancel_order_view, name='cancel_order'),
   path('feedback/', views.feedback_view, name='feedback'),
   path('Userprofile/', views.userprofile, name='UserProfile'),
   # path('buy-now/<uuid:uid>/', views.buy_now, name='buy_now'),
   # path('cart/increase/<str:uid>/', views.increase_quantity, name='increase_quantity'),
   # path('cart/decrease/<str:uid>/', views.decrease_quantity, name='decrease_quantity'),
   # path('checkout/initiate-razorpay/', views.initiate_razorpay_payment, name='initiate_razorpay'),
   # path('checkout/razorpay-callback/', views.razorpay_payment_callback, name='razorpay_callback'),
]