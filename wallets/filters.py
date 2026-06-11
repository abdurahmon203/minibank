import django_filters

from .models import BankCard


class BankCardFilter(django_filters.FilterSet):
    card_type = django_filters.CharFilter(field_name="card_type")
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = BankCard
        fields = ("card_type", "status")
