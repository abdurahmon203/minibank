from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "transaction_type",
        "amount",
        "commission",
        "total_amount",
        "currency",
        "status",
        "sender_wallet",
        "receiver_wallet",
        "created_at",
    )
    list_filter = ("transaction_type", "status", "currency", "created_at")
    search_fields = (
        "sender_wallet__wallet_number",
        "receiver_wallet__wallet_number",
        "description",
    )
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("sender_wallet", "receiver_wallet")
