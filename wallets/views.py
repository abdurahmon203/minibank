from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from common.pagination import CustomPagination

from .filters import BankCardFilter
from .models import BankCard, Wallet
from .serializers import BankCardSerializer, WalletSerializer


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.select_related("user").order_by("-created_at")
    serializer_class = WalletSerializer
    pagination_class = CustomPagination


class BankCardViewSet(viewsets.ModelViewSet):
    queryset = BankCard.objects.select_related("user").order_by("-created_at")
    serializer_class = BankCardSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = BankCardFilter
    search_fields = ("masked_pan", "card_holder")
