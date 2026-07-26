from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark as read
    notifications.filter(is_read=False).update(is_read=True)
    
    if request.user.role == 'ADMIN':
        base_template = 'custom_admin/admin_layout.html'
    elif request.user.role == 'COMPANY':
        base_template = 'company/company_base.html'
    else:
        base_template = 'candidate/candidate_base.html'
        
    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'base_template': base_template
    })

@login_required
def mark_all_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
