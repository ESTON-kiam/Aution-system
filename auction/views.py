from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Auction, Bid
from .permissions import IsCreatorOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    AuctionSerializer, BidSerializer,
    CreateAuctionSerializer, CreateBidSerializer
)


class AuctionListCreateView(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateAuctionSerializer
        return AuctionSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class AuctionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [IsCreatorOrReadOnly | IsAdminOrReadOnly]


class BidCreateView(generics.CreateAPIView):
    queryset = Bid.objects.all()
    serializer_class = CreateBidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        auction_id = kwargs.get('pk')
        try:
            auction = Auction.objects.get(pk=auction_id)
        except Auction.DoesNotExist:
            return Response(
                {'detail': 'Auction not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        auction.check_auction_status()

        if not auction.is_active:
            return Response(
                {'detail': 'This auction is closed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if auction.creator == request.user:
            return Response(
                {'detail': 'You cannot bid on your own auction.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        if amount <= auction.current_price:
            return Response(
                {'detail': 'Bid must be higher than current price.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        bid = serializer.save(auction=auction, bidder=request.user)
        auction.current_price = amount
        auction.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            BidSerializer(bid).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class UserBidsListView(generics.ListAPIView):  # Fixed typo: generics (not generics)
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bid.objects.filter(bidder=self.request.user)


class UserAuctionsListView(generics.ListAPIView):
    serializer_class = AuctionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Auction.objects.filter(creator=self.request.user)
