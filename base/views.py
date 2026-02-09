from django.shortcuts import render

# Create your views here.
from .models import MyUser

def custom_user_context(request):
    user = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = MyUser.objects.get(id=user_id)
        except MyUser.DoesNotExist:
            user = None
    return {'custom_user': user}