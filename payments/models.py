from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

from transactions.models import Transaction
from wallets.models import Wallet


class PaymentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    category = models.ForeignKey(
        PaymentCategory,
        on_delete=models.CASCADE,
        related_name="providers",
    )
    name = models.CharField(max_length=100)
    account_mask = models.CharField(max_length=100)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def calculate_commission(self, amount):
        return (amount * self.commission_percent / Decimal("100")).quantize(
            Decimal("0.01")
        )


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "PENDING"
        SUCCESS = "SUCCESS", "SUCCESS"
        FAILED = "FAILED", "FAILED"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payments"
    )
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="payments"
    )
    provider = models.ForeignKey(
        ServiceProvider, on_delete=models.CASCADE, related_name="payments"
    )
    account_number = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_record",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider.name} - {self.amount}"


class FavoritePayment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorite_payments"
    )
    provider = models.ForeignKey(
        ServiceProvider, on_delete=models.CASCADE, related_name="favorites"
    )
    title = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
