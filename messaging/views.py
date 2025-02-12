from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from django.http import JsonResponse

@login_required
def conversation_list(request):
    # Show all conversations for the logged-in user
    conversations = Conversation.objects.filter(participants=request.user).exclude(deleted_by=request.user)

    conversations = request.user.conversations.all()
    return render(request, 'messaging/conversation_list.html', {'conversations': conversations})

@login_required
def chat_view(request, conversation_id):
    # Get the conversation and its messages
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = conversation.messages.order_by('created_at')
    return render(request, 'messaging/chat.html', {'conversation': conversation, 'messages': messages})

@login_required
def delete_conversation(request, conversation_id):
    # Get the conversation; ensure the current user is a participant.
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user in conversation.participants.all():
        conversation.deleted_by.add(request.user)
        # Optionally, if all participants have deleted it, you can choose to delete the conversation entirely:
        if conversation.deleted_by.count() == conversation.participants.count():
            conversation.delete()
        return JsonResponse({"status": "deleted"})
    else:
        return JsonResponse({"error": "Unauthorized"}, status=403)