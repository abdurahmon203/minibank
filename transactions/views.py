from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import CustomPagination

from .filters import TransactionFilter
from .models import Transaction
from .serializers import (
    TopUpSerializer,
    TransactionSerializer,
    TransferSerializer,
    WithdrawSerializer,
)


class TransactionListAPIView(generics.ListAPIView):
    queryset = (
        Transaction.objects.select_related(
            "sender_wallet__user",
            "receiver_wallet__user",
        )
        .all()
        .order_by("-created_at")
    )
    serializer_class = TransactionSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TransactionFilter
    search_fields = (
        "sender_wallet__wallet_number",
        "receiver_wallet__wallet_number",
        "description",
    )


class TopUpAPIView(APIView):
    @extend_schema(request=TopUpSerializer, responses={201: TransactionSerializer})
    def post(self, request):
        serializer = TopUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()
        return Response(
            TransactionSerializer(transaction).data,
            status=status.HTTP_201_CREATED,
        )


class TransferAPIView(APIView):
    @extend_schema(request=TransferSerializer, responses={201: TransactionSerializer})
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()
        return Response(
            TransactionSerializer(transaction).data,
            status=status.HTTP_201_CREATED,
        )


class WithdrawAPIView(APIView):
    @extend_schema(request=WithdrawSerializer, responses={201: TransactionSerializer})
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()
        return Response(
            TransactionSerializer(transaction).data,
            status=status.HTTP_201_CREATED,
        )
