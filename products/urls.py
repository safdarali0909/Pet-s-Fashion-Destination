from django.urls import path
from products import views


urlpatterns = [
   path('get_products/<slug>/',views.get_products,name="get_products"),
   
]