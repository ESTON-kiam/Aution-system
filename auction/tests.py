from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Auction, Bid

User = get_user_model()


class AuctionAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        # Create an active auction
        self.active_auction = Auction.objects.create(
            title='Active Auction',
            description='This is an active auction',
            starting_price=100.00,
            current_price=100.00,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            creator=self.user1,
            is_active=True
        )

        # Create an expired auction
        self.expired_auction = Auction.objects.create(
            title='Expired Auction',
            description='This auction has ended',
            starting_price=50.00,
            current_price=50.00,
            start_time=timezone.now() - timezone.timedelta(days=1),
            end_time=timezone.now() - timezone.timedelta(hours=1),
            creator=self.user1,
            is_active=False
        )

        # Create a bid
        self.bid = Bid.objects.create(
            auction=self.active_auction,
            bidder=self.user2,
            amount=150.00
        )

    def test_auction_list(self):
        url = reverse('auction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_auction_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('auction-list')
        data = {
            'title': 'New Auction',
            'description': 'New auction description',
            'starting_price': 200.00,
            'start_time': timezone.now() - timezone.timedelta(minutes=10),
            'end_time': timezone.now() + timezone.timedelta(days=1)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Auction.objects.count(), 3)

    def test_place_bid_lower_than_current(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('bid-create', kwargs={'pk': self.active_auction.pk})
        data = {'amount': 50.00}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_place_bid_on_own_auction(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('bid-create', kwargs={'pk': self.active_auction.pk})
        data = {'amount': 200.00}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_auction_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('auction-detail', kwargs={'pk': self.active_auction.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Auction.objects.count(), 1)

    def test_delete_auction_as_other_user(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('auction-detail', kwargs={'pk': self.active_auction.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Auction.objects.count(), 2)

# Create your tests here.
