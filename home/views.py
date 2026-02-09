from django.shortcuts import render
from products.models import product,category
from itertools import groupby
from accounts.models import MyUser
from operator import attrgetter
from django.db.models import Q
# Create your views here.
def index(request):
    Product = product.objects.select_related('category').order_by('category_id')
    grouped_products = {}
    for category, items in groupby(Product, key=attrgetter('category')):
        grouped_products[category] = list(items)[:5]

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
            profile = None  # Handle if profile doesn't exist

    context = {
        'grouped_products': grouped_products,
        'custom_user': custom_user,
        'profile': profile,
        'products':Product
    }

    return render(request, 'home/index.html', context)
def about(request):
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
    context = {
       
        'custom_user': custom_user,
        'profile': profile
    }
    return render(request,'home/about.html',context)

def blog(request):
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
    context = {
       
        'custom_user': custom_user,
        'profile': profile
    }
    return render(request,'home/blog.html',context)

def category_products(request, slug):
    user_id = request.session.get('user_id')
    custom_user = None
    profile = None
 
    if user_id:
        try:
            custom_user = MyUser.objects.get(id=user_id)
            profile = custom_user.profile  # Try to access profile
        except MyUser.DoesNotExist:
            custom_user = None
        except profile.DoesNotExist:
            profile = None

    # IMPORTANT: change variable name to avoid conflict
    selected_category = category.objects.get(slug=slug)
    Products = product.objects.filter(category=selected_category)
    grouped_products ={
        category:list(items)
        for category, items in groupby(Products, key=lambda x: x.category)
        
     }
    return render(request, 'home/category_products.html', {
        'grouped_products': grouped_products,
        'category': selected_category,
        'products': Products,
        'custom_user': custom_user,
        'profile': profile,
    })
def search_products(request):
    query = request.GET.get('q', '')
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

    # Search by product name or category name
    products = product.objects.select_related('category').filter(
        Q(product_name__icontains=query) |
        Q(category__category_name__icontains=query)
    ).order_by('category_id')

    # Group products by category
    grouped_products = {
        category: list(items)
        for category, items in groupby(products, key=lambda x: x.category)
    }

    context = {
        'query': query,
        'products': products,
        'grouped_products': grouped_products,
        'custom_user': custom_user,
        'profile': profile,
    }
    return render(request, 'home/search_results.html', context)
