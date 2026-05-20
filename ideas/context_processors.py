from .models import Message
from django.db.models import Q

def unread_messages_context(request):
    if not request.user.is_authenticated:
        return {'global_unread_count': 0}
        
    unread_count = Message.objects.filter(
        Q(conversation__request__user=request.user) | 
        Q(conversation__request__idea__author=request.user) |
        Q(conversation__participants=request.user),
        is_read=False
    ).exclude(sender=request.user).distinct().count()
    
    return {'global_unread_count': unread_count}

