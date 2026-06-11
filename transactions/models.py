from django.db import models
from wallets.models import Wallet


class Transaction(models.Model):

    class TransactionType(models.TextChoices):
        TOP_UP = "TOP_UP", "TOP_UP"
        TRANSFER = "TRANSFER", "TRANSFER"
        PAYMENT = "PAYMENT", "PAYMENT"
        WITHDRAW = "WITHDRAW", "WITHDRAW"

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "PENDING"
        SUCCESS = "SUCCESS", "SUCCESS"
        FAILED = "FAILED", "FAILED"
        CANCELLED = "CANCELLED", "CANCELLED"

    sender_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="sent_transactions",
        null=True,
        blank=True
    )

    receiver_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="received_transactions",
        null=True,
        blank=True
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    commission = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=3,
        default="TJS"
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"