from django.db import models
from django.contrib.auth.models import User
from base1.models import BaseModel
import uuid
from products.models import *
from django.utils import timezone
from datetime import timedelta
from products.models import *

class MyUser(models.Model):
    id = models.AutoField(primary_key=True) 
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.email

class Profile(BaseModel):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.ImageField(upload_to="static/profile", null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


    def get_cart_counter(self):
        return CartItems.objects.filter(cart__is_paid=False,cart__user=self.user).count()

class Cart(BaseModel):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name="carts")
    is_paid =models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.email
class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name="cart_items")
    product = models.ForeignKey(product, on_delete=models.SET_NULL,blank=True,null=True)
   
    quantity = models.PositiveIntegerField(default=1)

    def get_product_price(self):
        price=[self.product.price]

        
         
        return sum(price)
    def get_total_price(self):
        return self.quantity * self.get_product_price()
    
    def __str__(self):
        return self.cart.user.first_name
    

# class chceckout(BaseModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.first_name

class DeliveryAddress(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True,default="Unkown")
    contact_number = models.CharField(max_length=15,null=True,blank=True,default="Unkown")
    address = models.TextField(null=True, blank=True,default="Unkown")
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    
    def __str__(self):
        return f'{self.name}, {self.city}'
    
class RazorpayPayment(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    signature = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.order_id}"



class Order(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Order Placed')
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.IntegerField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)  
    payment_method = models.CharField(max_length=50, default='Razorpay')

    def save(self, *args, **kwargs):
        if not self.delivery_date:
            self.delivery_date = timezone.now().date() + timedelta(days=7)  
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'
    

                                      
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Feedback from {self.name} ({self.email})"

                             

    

    







