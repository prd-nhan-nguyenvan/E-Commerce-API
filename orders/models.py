from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pd", "Pending"),  # The order has been created but not yet submitted.
        ("sb", "Submitted"),  # The order has been submitted and is being processed.
        ("pr", "Preparing"),  # The order is being prepared for delivery.
        ("de", "Delivering"),  # The order is currently being delivered to the customer.
        ("cp", "Completed"),  # The order has been successfully delivered.
        ("df", "Delivery Failed"),  # The delivery attempt was unsuccessful.
        ("cn", "Canceled"),  # The order has been canceled by the user.
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="pd")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )  # Adjust 'your_app' to the actual app name
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order #{self.order.id}"
