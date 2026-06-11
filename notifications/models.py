from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        TRANSACTION = "TRANSACTION", "TRANSACTION"
        PAYMENT = "PAYMENT", "PAYMENT"
        SYSTEM = "SYSTEM", "SYSTEM"
        CARD = "CARD", "CARD"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title