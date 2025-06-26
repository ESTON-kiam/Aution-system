from rest_framework import serializers
from .models import Auction, Bid
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class BidSerializer(serializers.ModelSerializer):
    bidder = UserSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'bidder', 'amount', 'created_at']
        read_only_fields = ['id', 'bidder', 'created_at']


class AuctionSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    winner = UserSerializer(read_only=True)
    bids = BidSerializer(many=True, read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Auction
        fields = [
            'id', 'title', 'description', 'starting_price', 'current_price',
            'start_time', 'end_time', 'creator', 'winner', 'is_active',
            'created_at', 'updated_at', 'bids'
        ]
        read_only_fields = [
            'id', 'creator', 'current_price', 'winner', 'is_active',
            'created_at', 'updated_at', 'bids'
        ]


class CreateAuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'starting_price', 'start_time', 'end_time']


class CreateBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['amount']
