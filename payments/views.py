from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common.pagination import CustomPagination

from .filters import PaymentFilter, ServiceProviderFilter
from .models import FavoritePayment, Payment, PaymentCategory, ServiceProvider
from .serializers import (
    FavoritePaymentSerializer,
    PaymentCategorySerializer,
    PaymentSerializer,
    ServiceProviderSerializer,
)


class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.select_related("category").all()
    serializer_class = ServiceProviderSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ServiceProviderFilter
    search_fields = ("name", "category__name")


class FavoritePaymentViewSet(viewsets.ModelViewSet):
    queryset = FavoritePayment.objects.select_related(
        "user", "provider__category"
    ).all()
    serializer_class = FavoritePaymentSerializer
    pagination_class = CustomPagination


class PaymentListCreateAPIView(generics.ListCreateAPIView):
    queryset = (
        Payment.objects.select_related("user", "wallet", "provider__category")
        .all()
        .order_by("-created_at")
    )
    serializer_class = PaymentSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter


@extend_schema(
    methods=["GET"],
    responses=PaymentCategorySerializer(many=True),
    operation_id="payment_category_list",
)
@extend_schema(
    methods=["POST"],
    request=PaymentCategorySerializer,
    responses=PaymentCategorySerializer,
    operation_id="payment_category_create",
)
@api_view(["GET", "POST"])
def payment_category_list_create(request):
    if request.method == "GET":
        queryset = PaymentCategory.objects.all().order_by("name")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = PaymentCategorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = PaymentCategorySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    methods=["GET"],
    responses=PaymentCategorySerializer,
    operation_id="payment_category_retrieve",
)
@extend_schema(
    methods=["PUT", "PATCH"],
    request=PaymentCategorySerializer,
    responses=PaymentCategorySerializer,
    operation_id="payment_category_update",
)
@extend_schema(methods=["DELETE"], responses={204: None}, operation_id="payment_category_delete")
@api_view(["GET", "PUT", "PATCH", "DELETE"])
def payment_category_detail(request, pk):
    category = get_object_or_404(PaymentCategory, pk=pk)

    if request.method == "GET":
        serializer = PaymentCategorySerializer(category)
        return Response(serializer.data)

    if request.method == "DELETE":
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    partial = request.method == "PATCH"
    serializer = PaymentCategorySerializer(
        category, data=request.data, partial=partial
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
