from django.contrib import admin

from .models import BankCard, Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet_number",
        "user",
        "balance",
        "currency",
        "status",
        "created_at",
    )
    list_filter = ("currency", "status", "created_at")
    search_fields = ("wallet_number", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)


@admin.register(BankCard)
class BankCardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "masked_pan",
        "card_holder",
        "user",
        "card_type",
        "status",
        "expire_month",
        "expire_year",
        "created_at",
    )
    list_filter = ("card_type", "status", "created_at")
    search_fields = ("masked_pan", "card_holder", "user__username")
    readonly_fields = ("created_at",)
    raw_id_fields = ("user",)
