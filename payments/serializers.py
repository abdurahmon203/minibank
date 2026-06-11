from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from rest_framework import serializers

from common.serializers import UserShortSerializer
from notifications.models import Notification
from transactions.models import Transaction
from wallets.models import Wallet
from wallets.serializers import WalletSerializer

from .models import FavoritePayment, Payment, PaymentCategory, ServiceProvider


class PaymentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCategory
        fields = "__all__"


class PaymentCategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCategory
        fields = ("id", "name")


class ServiceProviderSerializer(serializers.ModelSerializer):
    category = PaymentCategoryShortSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=PaymentCategory.objects.all(),
        write_only=True,
    )

    class Meta:
        model = ServiceProvider
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    wallet = WalletSerializer(read_only=True)
    provider = ServiceProviderSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=User.objects.all(),
        write_only=True,
    )
    wallet_id = serializers.PrimaryKeyRelatedField(
        source="wallet",
        queryset=Wallet.objects.all(),
        write_only=True,
    )
    provider_id = serializers.PrimaryKeyRelatedField(
        source="provider",
        queryset=ServiceProvider.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = (
            "commission",
            "total_amount",
            "status",
            "transaction",
            "created_at",
        )

    def validate_account_number(self, value):
        if not value.strip():
            raise serializers.ValidationError("Account number is required.")
        return value

    def validate(self, attrs):
        provider = attrs.get("provider") or getattr(self.instance, "provider", None)
        wallet = attrs.get("wallet") or getattr(self.instance, "wallet", None)
        amount = attrs.get("amount") or getattr(self.instance, "amount", None)
        account_number = attrs.get("account_number") or getattr(
            self.instance, "account_number", None
        )

        if account_number is not None and not str(account_number).strip():
            raise serializers.ValidationError(
                {"account_number": "Account number is required."}
            )

        if provider and not provider.is_active:
            raise serializers.ValidationError(
                {"provider": "Provider must be active."}
            )

        if provider and amount is not None:
            if amount < provider.min_amount or amount > provider.max_amount:
                raise serializers.ValidationError(
                    {
                        "amount": (
                            f"Amount must be between {provider.min_amount} "
                            f"and {provider.max_amount}."
                        )
                    }
                )

        if wallet:
            if wallet.status != Wallet.StatusChoices.ACTIVE:
                raise serializers.ValidationError(
                    {"wallet": "Wallet must be ACTIVE."}
                )

            if provider and amount is not None:
                commission = provider.calculate_commission(amount)
                total_amount = amount + commission
                if wallet.balance < total_amount:
                    raise serializers.ValidationError(
                        {"amount": "Insufficient wallet balance."}
                    )
                attrs["commission"] = commission
                attrs["total_amount"] = total_amount

        return attrs

    def create(self, validated_data):
        wallet = validated_data["wallet"]
        provider = validated_data["provider"]
        amount = validated_data["amount"]
        commission = validated_data.get("commission") or provider.calculate_commission(
            amount
        )
        total_amount = validated_data.get("total_amount") or (amount + commission)

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

            if wallet.balance < total_amount:
                raise serializers.ValidationError(
                    {"amount": "Insufficient wallet balance."}
                )

            wallet.balance -= total_amount
            wallet.save(update_fields=["balance", "updated_at"])

            txn = Transaction.objects.create(
                sender_wallet=wallet,
                transaction_type=Transaction.TransactionType.PAYMENT,
                amount=amount,
                commission=commission,
                total_amount=total_amount,
                currency=wallet.currency,
                status=Transaction.StatusChoices.SUCCESS,
                description=f"Payment to {provider.name}",
            )

            payment = Payment.objects.create(
                user=validated_data["user"],
                wallet=wallet,
                provider=provider,
                account_number=validated_data["account_number"],
                amount=amount,
                commission=commission,
                total_amount=total_amount,
                status=Payment.StatusChoices.SUCCESS,
                transaction=txn,
            )

            Notification.objects.create(
                user=validated_data["user"],
                title="Пардохт",
                message=(
                    f"Пардохти {total_amount:.2f} {wallet.currency} "
                    f"ба {provider.name} иҷро шуд."
                ),
                notification_type=Notification.NotificationType.PAYMENT,
            )

        return payment

    def to_representation(self, instance):
        data = super().to_representation(instance)
        currency = instance.wallet.currency
        data["amount"] = f"{instance.amount:.2f} {currency}"
        data["commission"] = f"{instance.commission:.2f} {currency}"
        data["total_amount"] = f"{instance.total_amount:.2f} {currency}"
        return data


class FavoritePaymentSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    provider = ServiceProviderSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=User.objects.all(),
        write_only=True,
    )
    provider_id = serializers.PrimaryKeyRelatedField(
        source="provider",
        queryset=ServiceProvider.objects.all(),
        write_only=True,
    )

    class Meta:
        model = FavoritePayment
        fields = "__all__"

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value

    def validate_account_number(self, value):
        if not value.strip():
            raise serializers.ValidationError("Account number is required.")
        return value

    def validate_provider(self, provider):
        if not provider.is_active:
            raise serializers.ValidationError("Provider must be active.")
        return provider
