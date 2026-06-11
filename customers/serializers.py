from django.contrib.auth.models import User
from rest_framework import serializers

from common.serializers import UserShortSerializer

from .models import CustomerProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=User.objects.all(),
        write_only=True,
    )

    class Meta:
        model = CustomerProfile
        fields = "__all__"