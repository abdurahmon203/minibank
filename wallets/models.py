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


class BankCard(models.Model):

    class CardType(models.TextChoices):
        VISA = "VISA", "VISA"
        MASTERCARD = "MASTERCARD", "MASTERCARD"
        KORTI_MILLI = "KORTI_MILLI", "KORTI_MILLI"
        OTHER = "OTHER", "OTHER"

    class StatusChoices(models.TextChoices):
        ACTIVE = "ACTIVE", "ACTIVE"
        BLOCKED = "BLOCKED", "BLOCKED"
        EXPIRED = "EXPIRED", "EXPIRED"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cards")

    card_holder = models.CharField(max_length=255)

    masked_pan = models.CharField(max_length=25)

    card_type = models.CharField(max_length=20, choices=CardType.choices)

    expire_month = models.PositiveSmallIntegerField()

    expire_year = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.masked_pan
