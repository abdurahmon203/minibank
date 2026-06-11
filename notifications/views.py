from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from common.pagination import CustomPagination

from .filters import NotificationFilter
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related("user").all().order_by("-created_at")
    serializer_class = NotificationSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter
