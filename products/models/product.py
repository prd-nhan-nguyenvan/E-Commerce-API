from django.db import models
from django.utils.text import slugify

from products.utils import upload_to


class Product(models.Model):
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    on_sell = models.BooleanField(default=0)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}_{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        ordering = ["-created_at", "-updated_at", "name"]

        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["category"]),
            models.Index(fields=["price"]),
            models.Index(fields=["sell_price"]),
        ]
