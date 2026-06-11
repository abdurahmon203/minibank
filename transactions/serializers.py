from decimal import Decimal

from django.db import transaction as db_transaction
from rest_framework import serializers

from common.serializers import UserShortSerializer
from notifications.models import Notification
from wallets.models import Wallet

from .models import Transaction


class WalletShortSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)

    class Meta:
        model = Wallet
        fields = ("id", "wallet_number", "user")


class TransactionSerializer(serializers.ModelSerializer):
    sender_wallet = WalletShortSerializer(read_only=True)
    receiver_wallet = WalletShortSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"

    def validate_amount(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate(self, attrs):
        sender = attrs.get("sender_wallet") or getattr(
            self.instance, "sender_wallet", None
        )
        receiver = attrs.get("receiver_wallet") or getattr(
            self.instance, "receiver_wallet", None
        )

        if sender and receiver and sender == receiver:
            raise serializers.ValidationError(
                {"receiver_wallet": "Sender and receiver must be different."}
            )

        amount = attrs.get("amount") or getattr(self.instance, "amount", None)
        wallets_to_check = [wallet for wallet in (sender, receiver) if wallet]

        for wallet in wallets_to_check:
            if wallet.status != Wallet.StatusChoices.ACTIVE:
                raise serializers.ValidationError(
                    f"Wallet {wallet.wallet_number} must be ACTIVE."
                )

        if sender and amount and sender.balance < amount:
            raise serializers.ValidationError(
                {"amount": "Insufficient wallet balance."}
            )

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)

        type_map = {
            "TOP_UP": "Пуркунии баланс",
            "TRANSFER": "Интиқоли пул",
            "PAYMENT": "Пардохт",
            "WITHDRAW": "Бардошти пул",
        }
        status_map = {
            "PENDING": "Дар интизорӣ",
            "SUCCESS": "Иҷро шуд",
            "FAILED": "Ноком шуд",
            "CANCELLED": "Бекор шуд",
        }

        data["transaction_type"] = type_map.get(
            instance.transaction_type, instance.transaction_type
        )
        data["status"] = status_map.get(instance.status, instance.status)
        data["amount"] = f"{instance.amount:.2f} {instance.currency}"
        data["commission"] = f"{instance.commission:.2f} {instance.currency}"
        data["total_amount"] = f"{instance.total_amount:.2f} {instance.currency}"

        return data


class TopUpSerializer(serializers.Serializer):
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_amount(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_wallet(self, wallet):
        if wallet.status != Wallet.StatusChoices.ACTIVE:
            raise serializers.ValidationError("Wallet must be ACTIVE.")
        return wallet

    def create(self, validated_data):
        wallet = validated_data["wallet"]
        amount = validated_data["amount"]
        description = validated_data.get("description", "Top up")

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
            wallet.balance += amount
            wallet.save(update_fields=["balance", "updated_at"])

            txn = Transaction.objects.create(
                receiver_wallet=wallet,
                transaction_type=Transaction.TransactionType.TOP_UP,
                amount=amount,
                commission=Decimal("0"),
                total_amount=amount,
                currency=wallet.currency,
                status=Transaction.StatusChoices.SUCCESS,
                description=description,
            )

            Notification.objects.create(
                user=wallet.user,
                title="Пуркунии баланс",
                message=f"Ба ҳисоби шумо {amount:.2f} {wallet.currency} илова шуд.",
                notification_type=Notification.NotificationType.TRANSACTION,
            )

        return txn


class TransferSerializer(serializers.Serializer):
    sender_wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    receiver_wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_amount(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate(self, attrs):
        sender = attrs["sender_wallet"]
        receiver = attrs["receiver_wallet"]
        amount = attrs["amount"]

        if sender == receiver:
            raise serializers.ValidationError(
                {"receiver_wallet": "Sender and receiver must be different."}
            )

        for wallet in (sender, receiver):
            if wallet.status != Wallet.StatusChoices.ACTIVE:
                raise serializers.ValidationError(
                    f"Wallet {wallet.wallet_number} must be ACTIVE."
                )

        if sender.balance < amount:
            raise serializers.ValidationError(
                {"amount": "Insufficient wallet balance."}
            )

        return attrs

    def create(self, validated_data):
        sender = validated_data["sender_wallet"]
        receiver = validated_data["receiver_wallet"]
        amount = validated_data["amount"]
        description = validated_data.get("description", "Transfer")

        with db_transaction.atomic():
            sender = Wallet.objects.select_for_update().get(pk=sender.pk)
            receiver = Wallet.objects.select_for_update().get(pk=receiver.pk)

            if sender.balance < amount:
                raise serializers.ValidationError(
                    {"amount": "Insufficient wallet balance."}
                )

            sender.balance -= amount
            receiver.balance += amount
            sender.save(update_fields=["balance", "updated_at"])
            receiver.save(update_fields=["balance", "updated_at"])

            txn = Transaction.objects.create(
                sender_wallet=sender,
                receiver_wallet=receiver,
                transaction_type=Transaction.TransactionType.TRANSFER,
                amount=amount,
                commission=Decimal("0"),
                total_amount=amount,
                currency=sender.currency,
                status=Transaction.StatusChoices.SUCCESS,
                description=description,
            )

            Notification.objects.create(
                user=sender.user,
                title="Интиқоли пул",
                message=(
                    f"Аз ҳисоби шумо {amount:.2f} {sender.currency} "
                    f"ба {receiver.wallet_number} интиқол дода шуд."
                ),
                notification_type=Notification.NotificationType.TRANSACTION,
            )
            Notification.objects.create(
                user=receiver.user,
                title="Қабули пул",
                message=(
                    f"Ба ҳисоби шумо {amount:.2f} {receiver.currency} "
                    f"аз {sender.wallet_number} ворид шуд."
                ),
                notification_type=Notification.NotificationType.TRANSACTION,
            )

        return txn


class WithdrawSerializer(serializers.Serializer):
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_amount(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_wallet(self, wallet):
        if wallet.status != Wallet.StatusChoices.ACTIVE:
            raise serializers.ValidationError("Wallet must be ACTIVE.")
        return wallet

    def validate(self, attrs):
        wallet = attrs["wallet"]
        amount = attrs["amount"]
        if wallet.balance < amount:
            raise serializers.ValidationError(
                {"amount": "Insufficient wallet balance."}
            )
        return attrs

    def create(self, validated_data):
        wallet = validated_data["wallet"]
        amount = validated_data["amount"]
        description = validated_data.get("description", "Withdraw")

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

            if wallet.balance < amount:
                raise serializers.ValidationError(
                    {"amount": "Insufficient wallet balance."}
                )

            wallet.balance -= amount
            wallet.save(update_fields=["balance", "updated_at"])

            txn = Transaction.objects.create(
                sender_wallet=wallet,
                transaction_type=Transaction.TransactionType.WITHDRAW,
                amount=amount,
                commission=Decimal("0"),
                total_amount=amount,
                currency=wallet.currency,
                status=Transaction.StatusChoices.SUCCESS,
                description=description,
            )

        return txn
