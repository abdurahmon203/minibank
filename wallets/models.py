from django.db import models
from django.contrib.auth.models import User


class Wallet(models.Model):

    class CurrencyChoices(models.TextChoices):
        TJS = "TJS", "TJS"
        USD = "USD", "USD"
        RUB = "RUB", "RUB"

    class StatusChoices(models.TextChoices):
        ACTIVE = "ACTIVE", "ACTIVE"
        BLOCKED = "BLOCKED", "BLOCKED"
        CLOSED = "CLOSED", "CLOSED"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")

    wallet_number = models.CharField(max_length=20, unique=True)

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    currency = models.CharField(
        max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.TJS
    )

    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, default=StatusChoices.ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.wallet_number
