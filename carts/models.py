# carts/models.py
from django.conf import settings
from django.db import models

from authentication.models import CustomUser as User
from products.models import Product


class Cart(models.Model):
    user: User = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    objects = models.Manager()

    def __str__(self):
        return f"Cart of {self.user.email}"


class CartItem(models.Model):
    cart: Cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    objects = models.Manager()

    class Meta:
        unique_together = ["cart", "product"]

    def __str__(self):
        return (
            f"{self.quantity} of {self.product.name} in {self.cart.user.email}'s cart"
        )
