from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Conversation(models.Model):
    # Each conversation is tied to an auction (if desired)
    auction = models.ForeignKey('auctions.Auction', on_delete=models.CASCADE, related_name='conversations')
    deleted_by = models.ManyToManyField(User, related_name="deleted_conversations", blank=True)
    # Participants in the conversation (typically the seller and the winning bidder)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        participant_names = ", ".join(user.username for user in self.participants.all())
        return f"Conversation for {self.auction.title} ({participant_names})"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)  # Optionally track read/unread status

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
