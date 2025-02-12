from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from .models import Auction
#from auction_platform.celery_app import app

import logging

logger = logging.getLogger(__name__)  # 🔍 Add logging
@shared_task
def check_expired_auctions():
    try:
        expired_auctions = Auction.objects.filter(end_time__lte=now(), status="open")
        logger.info(f"✅ Found {expired_auctions.count()} expired auctions.")
        
        for auction in expired_auctions:
            winner = auction.get_highest_bidder()
            logger.info(f"Processing auction: {auction.title}, Winner: {winner}")
            
            if winner:
                auction.winner = winner
                auction.status = "closed"
                auction.save()
                from messaging.utils import create_conversation_for_auction
                create_conversation_for_auction(auction)

                logger.info(f"🎯 Auction '{auction.title}' closed. Winner: {winner.username}")

                if winner.email:
                    send_mail(
                        subject="Congratulations! You Won the Auction",
                        message=f"Congratulations {winner.username}! You won '{auction.title}' with a bid of ${auction.current_bid}.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[winner.email],
                    )
                else:
                    logger.warning(f"⚠️ Winner {winner.username} has no email address.")
                
                if auction.created_by.email:
                    send_mail(
                        subject="Your Auction Has Ended",
                        message=f"Your auction '{auction.title}' has ended. Winner: {winner.username} with a bid of ${auction.current_bid}.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[auction.created_by.email],
                    )
                else:
                    logger.warning(f"⚠️ Seller {auction.created_by.username} has no email address.")
            else:
                auction.status = "closed"
                auction.save()
                logger.warning(f"⚠️ Auction '{auction.title}' has no valid bids.")

        return "Task completed successfully"  # Ensure this is a simple string or integer.
    except Exception as e:
        logger.error(f"❌ Error in check_expired_auctions: {str(e)}")
        raise e
