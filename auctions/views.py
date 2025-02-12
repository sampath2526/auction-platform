from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Auction, Bid, UserProfile, Bookmark
from django.utils.timezone import now, localtime
from django.db.models import Q
from django.utils.timezone import make_aware
from django.utils.timezone import localtime
from django.contrib.auth import logout
from django.http import JsonResponse

from datetime import datetime

def auction_list(request):
    auctions = Auction.objects.filter(end_time__gte=now())
    
    search_query = request.GET.get("search", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    category = request.GET.get("category", "")
    status = request.GET.get("status", "")

    if search_query:
        auctions = auctions.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    if min_price:
        auctions = auctions.filter(current_bid__gte=min_price)
    if max_price:
        auctions = auctions.filter(current_bid__lte=max_price)
    if category:
        auctions = auctions.filter(category__iexact=category)
    if status:
        auctions = auctions.filter(status__iexact=status)
    for auction in auctions:
        remaining_time = auction.end_time - now()
        auction.remaining_days = max(remaining_time.days, 0)
        auction.remaining_hours = max(remaining_time.seconds // 3600, 0)
        auction.remaining_minutes = max((remaining_time.seconds % 3600) // 60, 0)
        
       
        highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
        auction.highest_bidder = highest_bid.user if highest_bid else None 
        auction.save()
         
    return render(request, "auctions/auction_list.html", {"auctions": auctions})

@login_required
def create_auction(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        starting_bid = request.POST['starting_bid']
        end_time_str = request.POST['end_time']
        category = request.POST['category']
        image = request.FILES.get('image')
        end_time = make_aware(datetime.fromisoformat(end_time_str))  # Convert to UTC


        auction = Auction.objects.create(
            title=title,
            description=description,
            starting_bid=starting_bid,
            current_bid=starting_bid,
            end_time=end_time,
            category=category,
            created_by=request.user,
            image=image  # Save the image field

        )
        return redirect('auction_list')
    return render(request, 'auctions/create_auction.html')

@login_required
def place_bid(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)

    # Calculate remaining time
    remaining_time = localtime(auction.end_time) - localtime(now())
    auction.remaining_days = max(remaining_time.days, 0)
    auction.remaining_hours = max(remaining_time.seconds // 3600, 0)
    auction.remaining_minutes = max((remaining_time.seconds % 3600) // 60, 0)
    # Get the highest bid and bidder (initially before bid placement)
    highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
    auction.highest_bidder = highest_bid.user if highest_bid else None
    is_bookmarked = Bookmark.objects.filter(user=request.user, auction=auction).exists()

    if request.method == "POST":
        bid_amount = request.POST.get('bid_amount')

        # Validate bid amount
        if bid_amount and float(bid_amount) > auction.current_bid:
            bid_amount = float(bid_amount)

            # Save the new bid
            Bid.objects.create(auction=auction, user=request.user, amount=bid_amount)
            print(f"New bid created: Auction ID: {auction.id}, User: {request.user}, Amount: {bid_amount}")

            # Update auction's current bid
            auction.current_bid = bid_amount
            auction.save()

            # Recalculate the highest bidder after the new bid
            highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
            auction.highest_bidder = highest_bid.user if highest_bid else None
            auction.save()

            # Broadcast updates via WebSocket for real-time updates
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(  # for the specific auction
                f"auction_{auction.id}",
                {
                    'type': 'auction_bid',
                    'bid': auction.current_bid,
                    'highest_bidder': auction.highest_bidder.username if auction.highest_bidder else None
                }
            )

            async_to_sync(channel_layer.group_send)(  # for all auctions
                "auctions_updates",
                {
                    'type': 'auctions_update',
                    'auction_id': auction.id,
                    'current_bid': auction.current_bid,
                    'highest_bidder': auction.highest_bidder.username if auction.highest_bidder else None
                }
            )

            return redirect('auction_list')

        else:
            return render(request, 'auctions/place_bid.html', {
                'auction': auction,
                'error': "Bid must be higher than the current bid.",
            })

    return render(request, 'auctions/place_bid.html', {
        'auction': auction,
        'highest_bidder': auction.highest_bidder,
        'remaining_days': auction.remaining_days,
        'remaining_hours': auction.remaining_hours,
        'remaining_minutes': auction.remaining_minutes,
        'is_bookmarked': is_bookmarked
    })

@login_required
def toggle_bookmark(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, auction=auction)

    if not created:  # If bookmark already exists, remove it (toggle off)
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True

    return JsonResponse({"is_bookmarked": is_bookmarked})



@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_auctions = Auction.objects.filter(created_by=request.user)
    bookmarked_auctions = Auction.objects.filter(bookmark__user=request.user)

    return render(request, "auctions/profile.html", {"profile": profile, "user_auctions": user_auctions, "bookmarked_auctions": bookmarked_auctions,})

def logout_view(request):
    logout(request)
    return redirect("home")  # Redirect to homepage after logout