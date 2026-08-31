from chat.models import ChatMessage

def unread_messages_count(request):
    if request.user.is_authenticated:
        # Get count of unread messages in threads where the user is a participant,
        # but the message was not sent by the user.
        count = ChatMessage.objects.filter(
            thread__employer=request.user, 
            is_read=False
        ).exclude(sender=request.user).count() + ChatMessage.objects.filter(
            thread__candidate=request.user, 
            is_read=False
        ).exclude(sender=request.user).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}
