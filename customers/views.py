from rest_framework import viewsets

from common.pagination import CustomPagination

from .models import CustomerProfile
from .serializers import CustomerProfileSerializer


class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.select_related("user").order_by("-created_at")
    serializer_class = CustomerProfileSerializer
    pagination_class = CustomPagination
