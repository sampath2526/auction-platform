from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import datetime
from django.utils.timezone import is_aware, make_aware


class Auction(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_auctions")  # Make sure this exists
    bookmarked_by = models.ManyToManyField(User, related_name="bookmarked_auctions", blank=True)
    category = models.CharField(max_length=50, choices=[('electronics', 'Electronics'), ('furniture', 'Furniture'),
                                                        ('art', 'Art'), ('fashion', 'Fashion'), ('vehicles', 'Vehicles')],
                                default='electronics')
    status = models.CharField(max_length=10, choices=[('open', 'Open'), ('closed', 'Closed')], default='open')
    image = models.ImageField(upload_to='auction_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
     if self.end_time and self.end_time <= now():
        self.status = 'closed'
     super().save(*args, **kwargs)



    def __str__(self):
        return self.title
    
    def is_expired(self):
        """Check if auction has ended"""
        return now() >= self.end_time
    
    def get_highest_bidder(self):
     try:
        highest_bid = self.bids.order_by('-amount').first()
        if highest_bid:
            return highest_bid.user
        else:
            return None
     except Exception as e:
        # Log and return None if there's an error
        print(f"Error in get_highest_bidder for auction '{self.title}': {e}")
        return None


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return self.user.username

    
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} bookmarked {self.auction.title}"
