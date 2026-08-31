from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from applications.models import Applications
from .models import ChatThread, ChatMessage

@login_required
def start_chat_view(request, application_id):
    application = get_object_or_404(Applications, id=application_id)
    
    # Ensure the user is the employer who posted the job
    if application.job.company.user != request.user:
        return HttpResponseForbidden("You are not authorized to start a chat for this application.")
        
    thread, created = ChatThread.objects.get_or_create(
        employer=request.user,
        candidate=application.candidate.user,
        job=application.job
    )
    
    return redirect('chat:chat_room', thread_id=thread.id)

@login_required
def inbox_view(request):
    threads = ChatThread.objects.filter(
        Q(employer=request.user) | Q(candidate=request.user)
    ).order_by('-updated_at')
    
    base_template = 'company/company_base.html' if request.user.role == 'COMPANY' else 'candidate/candidate_base.html'
    
    context = {
        'threads': threads,
        'base_template': base_template
    }
    return render(request, 'chat/inbox.html', context)

@login_required
def chat_room_view(request, thread_id):
    thread = get_object_or_404(ChatThread, id=thread_id)
    
    # Verify user is part of the thread
    if request.user != thread.employer and request.user != thread.candidate:
        return HttpResponseForbidden("You are not authorized to view this chat.")
        
    # Mark messages from the other user as read
    thread.messages.exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            msg = ChatMessage.objects.create(
                thread=thread,
                sender=request.user,
                message=message_text
            )
            # update thread updated_at
            thread.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': msg.message,
                    'sender': msg.sender.username,
                    'timestamp': msg.timestamp.strftime('%b %d, %Y %I:%M %p')
                })
            
            return redirect('chat:chat_room', thread_id=thread.id)
    
    # Get all threads for the sidebar (inbox)
    threads = ChatThread.objects.filter(
        Q(employer=request.user) | Q(candidate=request.user)
    ).order_by('-updated_at')
            
    base_template = 'company/company_base.html' if request.user.role == 'COMPANY' else 'candidate/candidate_base.html'
            
    context = {
        'thread': thread,
        'threads': threads,
        'messages': thread.messages.all(),
        'base_template': base_template
    }
    return render(request, 'chat/messages.html', context)
