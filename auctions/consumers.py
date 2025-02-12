import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs'].get('auction_id', None)
        if self.auction_id:
            self.auction_group_name = f"auction_{self.auction_id}"
            print(f"Client connected to group: {self.auction_group_name}, channel: {self.channel_name}")
            await self.channel_layer.group_add(self.auction_group_name, self.channel_name)

        print(f"Client connected to group: auctions_updates, channel: {self.channel_name}")
        await self.channel_layer.group_add("auctions_updates", self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'auction_group_name'):
            await self.channel_layer.group_discard(self.auction_group_name, self.channel_name)

        await self.channel_layer.group_discard("auctions_updates", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        bid = data['bid']
        print(f"Received bid: {bid}")

        bid_updated, highest_bidder = await self.update_bid(self.auction_id, bid)

        if bid_updated:
            if hasattr(self, 'auction_group_name'):
                await self.channel_layer.group_send(
                    self.auction_group_name,
                    {
                        'type': 'auction_bid',
                        'bid': bid,
                        'highest_bidder': highest_bidder
                    }
                )

            await self.channel_layer.group_send(
                "auctions_updates",
                {
                    'type': 'auctions_update',
                    'auction_id': self.auction_id,
                    'current_bid': bid,
                    'highest_bidder': highest_bidder
                }
            )

    async def auction_bid(self, event):
        bid = event['bid']
        highest_bidder = event['highest_bidder']
        print(f"Broadcasting bid: {bid}, Highest bidder: {highest_bidder} to auction group.")
        await self.send(text_data=json.dumps({
            'bid': bid,
            'highest_bidder': highest_bidder
        }))

    async def auctions_update(self, event):
        auction_id = event['auction_id']
        current_bid = event['current_bid']
        highest_bidder = event['highest_bidder']
        print(f"Broadcasting update for auction {auction_id} with bid {current_bid} and highest bidder {highest_bidder}.")
        await self.send(text_data=json.dumps({
            'auction_id': auction_id,
            'current_bid': current_bid,
            'highest_bidder': highest_bidder
        }))

    @sync_to_async(thread_sensitive=True)
    def update_bid(self, auction_id, bid):
     from .models import Auction, Bid
     try:
        auction = Auction.objects.get(id=auction_id)
        # Get the current user from the scope
        user = self.scope["user"]
        if bid > auction.current_bid:
            # Update the auction's current bid
            auction.current_bid = bid
            auction.save()
            # Create a new Bid record
            Bid.objects.create(auction=auction, user=user, amount=bid)
            # Recalculate the highest bid and highest bidder
            highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
            highest_bidder_username = highest_bid.user.username if highest_bid else None
            print(f"Auction {auction_id} updated with new bid: {bid} and highest bidder: {highest_bidder_username}")
            return True, highest_bidder_username
        else:
            print("Bid is not higher than the current bid.")
            return False, None
     except Auction.DoesNotExist:
        print(f"Auction {auction_id} does not exist.")
        return False, None
