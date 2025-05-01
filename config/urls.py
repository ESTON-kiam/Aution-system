from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from auction import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="Auction API",
        default_version='v1',
        description="API for managing auctions and bids",
    ),
    public=True,
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auctions/', views.AuctionListCreateView.as_view(), name='auction-list'),
    path('api/auctions/<int:pk>/', views.AuctionDetailView.as_view(), name='auction-detail'),
    path('api/auctions/<int:pk>/bids/', views.BidCreateView.as_view(), name='bid-create'),
    path('api/my-bids/', views.UserBidsListView.as_view(), name='user-bids'),
    path('api/my-auctions/', views.UserAuctionsListView.as_view(), name='user-auctions'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]




