from celery import shared_task
from django.utils import timezone
from .models import Auction


@shared_task
def close_expired_auctions():
    expired_auctions = Auction.objects.filter(
        end_time__lte=timezone.now(),
        is_active=True
    )

    for auction in expired_auctions:
        highest_bid = auction.bids.order_by('-amount').first()
        if highest_bid:
            auction.winner = highest_bid.bidder
        auction.is_active = False
        auction.save()