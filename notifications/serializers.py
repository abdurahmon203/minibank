from rest_framework import serializers

from common.serializers import UserShortSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=UserShortSerializer.Meta.model.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Notification
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["status_text"] = (
            "Хонда шуд" if instance.is_read else "Хонда нашудааст"
        )
        return data
