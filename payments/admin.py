from django.contrib import admin

from .models import FavoritePayment, Payment, PaymentCategory, ServiceProvider


@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at",)


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "min_amount",
        "max_amount",
        "commission_percent",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("name", "account_mask", "category__name")
    readonly_fields = ("created_at",)
    raw_id_fields = ("category",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "wallet",
        "provider",
        "account_number",
        "amount",
        "commission",
        "total_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "provider", "created_at")
    search_fields = (
        "account_number",
        "user__username",
        "wallet__wallet_number",
        "provider__name",
    )
    readonly_fields = ("created_at",)
    raw_id_fields = ("user", "wallet", "provider", "transaction")


@admin.register(FavoritePayment)
class FavoritePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "provider",
        "account_number",
        "created_at",
    )
    list_filter = ("provider", "created_at")
    search_fields = ("title", "account_number", "user__username", "provider__name")
    readonly_fields = ("created_at",)
    raw_id_fields = ("user", "provider")
