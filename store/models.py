from django.db import models


class Order(models.Model):
    stripe_session_id = models.CharField(max_length=255, unique=True)
    amount = models.IntegerField()  # in cents
    items = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.stripe_session_id}"

