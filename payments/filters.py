import django_filters

from .models import Payment, ServiceProvider


class ServiceProviderFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category_id")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = ServiceProvider
        fields = ("category", "is_active")


class PaymentFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    provider = django_filters.NumberFilter(field_name="provider_id")
    wallet = django_filters.NumberFilter(field_name="wallet_id")

    class Meta:
        model = Payment
        fields = ("status", "provider", "wallet")
