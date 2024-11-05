import factory
from django.utils.text import slugify
from factory.django import DjangoModelFactory
from faker import Faker

from products.models import Category, Product

fake = Faker()


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("word")
    description = factory.Faker("sentence")


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    name = factory.Faker("word")
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    description = factory.Faker("sentence")
    price = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    sell_price = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, positive=True
    )
    on_sell = factory.Faker("boolean")
    stock = factory.Faker("random_int", min=0, max=1000)
    image = factory.django.ImageField(color=factory.Faker("safe_color_name"))
    created_at = factory.Faker("date_time_this_year")
    updated_at = factory.Faker("date_time_this_year")

    @factory.lazy_attribute
    def sell_price(self):
        """Ensure sell_price is equal to or less than price."""
        return min(
            fake.pydecimal(left_digits=5, right_digits=2, positive=True), self.price
        )
