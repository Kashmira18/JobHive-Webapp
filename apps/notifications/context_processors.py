from .models import Notification


def notification_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        unread_count = notifications.filter(is_read=False).count()
        latest_notifications = notifications[:5]
        return {
            'unread_notifications_count': unread_count,
            'latest_notifications': latest_notifications,
            'notifications': notifications,
        }
    return {
        'unread_notifications_count': 0,
        'latest_notifications': [],
        'notifications': [],
    }