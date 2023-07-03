from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from notification.models import Notification

    

# Create your views here.

""" All notifications """
@login_required
def ShowNotifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')
    context = {
        'notifications':notifications,
    }


    #  if user.is_depression:
    #     relatives = relative.objects.filter(user=user)
    #     for relative in relatives:
    #         # Create and save notifications for each relative
    #         notification = Notification.objects.create(user=relative.user, message="You have a relative with depression.")
    #         notification.save()

    return render(request, 'blog/notifications.html', context)