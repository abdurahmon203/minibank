import django_filters
from django.db.models import Q

from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    type = django_filters.CharFilter(field_name="transaction_type")
    wallet = django_filters.NumberFilter(method="filter_wallet")

    class Meta:
        model = Transaction
        fields = ("status", "type", "wallet")

    def filter_wallet(self, queryset, name, value):
        return queryset.filter(
            Q(sender_wallet_id=value) | Q(receiver_wallet_id=value)
        )
