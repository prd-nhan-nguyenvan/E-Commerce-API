from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pd", "Pending"),
        ("sb", "Submitted"),
        ("pr", "Preparing"),
        ("de", "Delivering"),
        ("cp", "Completed"),
        ("df", "Delivery Failed"),
        ("cn", "Canceled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="pd")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def can_change_status(self, new_status):
        if self.status == "pd" and new_status in ["sb", "cn"]:
            return True
        if self.status == "sb" and new_status in ["pr", "cn"]:
            return True
        if self.status == "pr" and new_status in ["de", "cn"]:
            return True
        if self.status == "de" and new_status in ["df", "cp"]:
            return True
        return False

    def update_status(self, new_status):
        if self.can_change_status(new_status):
            self.status = new_status
            self.save()
            return True
        return False

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"

    class Meta:
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )  # Adjust 'your_app' to the actual app name
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ["order", "product"]

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order #{self.order.id}"
