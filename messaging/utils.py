from .models import Conversation

def create_conversation_for_auction(auction):
    if auction.winner:
        conversation, created = Conversation.objects.get_or_create(auction=auction)
        conversation.participants.add(auction.created_by, auction.winner)
        conversation.save()
        return conversation
    return None
