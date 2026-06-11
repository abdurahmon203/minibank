import uuid
from datetime import date

from rest_framework import serializers

from common.serializers import UserShortSerializer

from .models import BankCard, Wallet


class WalletSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=UserShortSerializer.Meta.model.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Wallet
        fields = "__all__"
        read_only_fields = (
            "wallet_number",
            "balance",
            "created_at",
            "updated_at",
        )

    def validate_currency(self, value):
        valid = {choice.value for choice in Wallet.CurrencyChoices}
        if value not in valid:
            raise serializers.ValidationError(
                f"Currency must be one of: {', '.join(sorted(valid))}."
            )
        return value

    def validate_status(self, value):
        valid = {choice.value for choice in Wallet.StatusChoices}
        if value not in valid:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(sorted(valid))}."
            )
        return value

    def create(self, validated_data):
        validated_data["wallet_number"] = f"W{uuid.uuid4().hex[:12].upper()}"
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["balance"] = f"{instance.balance:.2f} {instance.currency}"
        return data


class BankCardSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=UserShortSerializer.Meta.model.objects.all(),
        write_only=True,
    )

    class Meta:
        model = BankCard
        fields = "__all__"

    def validate_expire_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError(
                "Expire month must be between 1 and 12."
            )
        return value

    def validate_expire_year(self, value):
        if value < date.today().year:
            raise serializers.ValidationError(
                "Card expiration year cannot be in the past."
            )
        return value

    def validate_masked_pan(self, value):
        if not value.strip():
            raise serializers.ValidationError("Masked PAN cannot be empty.")
        return value

    def validate_card_holder(self, value):
        if not value.strip():
            raise serializers.ValidationError("Card holder cannot be empty.")
        return value
