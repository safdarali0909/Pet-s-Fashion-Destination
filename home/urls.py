
from django.urls import path
from home import views


urlpatterns = [
   path('',views.index,name="Home"),
   path('about',views.about,name="About"),
   path('blog',views.blog,name="blog"),
   path('category/<slug>/', views.category_products, name='category_products'),
   path('search', views.search_products, name='search_products'),
]