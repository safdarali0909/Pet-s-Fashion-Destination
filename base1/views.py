from django.shortcuts import render
from .models import MyUser

def some_view(request):
    user = None
    if request.session.get('user_id'):
        try:
            user = MyUser.objects.get(id=request.session['user_id'])
        except MyUser.DoesNotExist:
            user = None

    context = {
        'custom_user': user  # pass this to template
    }
    return render(request, 'account/base.html', context)