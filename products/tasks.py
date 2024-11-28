import logging

import requests
from celery import shared_task
from django.core.files.base import ContentFile
from django.template.defaultfilters import slugify
from elasticsearch.exceptions import NotFoundError

from products.documents import ProductDocument
from products.models import Category, Product
from products.utils import invalidate_product_cache

logger = logging.getLogger(__name__)


@shared_task
def bulk_import_products(product_data_list):
    products = []
    categories_cache = {}
    failed_imports = []

    for row in product_data_list:
        try:

            category_name = row["category_name"]
            category = (
                categories_cache.get(category_name)
                or Category.objects.get_or_create(name=category_name)[0]
            )
            categories_cache[category_name] = category

            slug = slugify(row["name"])

            if len(slug) > 50:
                slug = slug[:50]
            counter = 1
            original_slug = slug
            while Product.objects.filter(slug=slug).exists() or any(
                p.slug == slug for p in products
            ):
                counter += 1
                slug = f"{original_slug}_{counter}"

            product = Product(
                name=row["name"],
                description=row.get("description", ""),
                price=row.get("price", 0),
                sell_price=row.get("sell_price", 0),
                on_sell=row.get("on_sell", False),
                stock=row.get("stock", 0),
                category=category,
                slug=slug,
            )

            if "image_url" in row and row["image_url"]:
                try:
                    image_response = requests.get(row["image_url"], timeout=10)
                    if image_response.status_code == 200:
                        product.image.save(
                            f"{slugify(product.name)}.jpg",
                            ContentFile(image_response.content),
                            save=False,
                        )
                    else:
                        logger.warning(
                            f"Failed to fetch image for {row['name']}, status code: {image_response.status_code}"
                        )
                except Exception as e:
                    logger.error(f"Error fetching image for {row['name']}: {e}")

            products.append(product)

        except Exception as e:
            logger.error(f"Error processing product {row['name']}: {e}")
            failed_imports.append(row)

    if products:
        try:
            Product.objects.bulk_create(products, batch_size=100)
            logger.info(f"Successfully imported {len(products)} products.")
            invalidate_product_cache()
        except Exception as e:
            logger.error(f"Error during bulk creation of products: {e}")

    if failed_imports:
        logger.error(
            f"Failed to import {len(failed_imports)} products: {failed_imports}"
        )

    return len(products), len(failed_imports)


@shared_task
def index_product_task(product_id):
    product = Product.objects.get(id=product_id)
    category = product.category

    category_data = {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
    }

    product_doc = ProductDocument(
        meta={"id": product.id},
        name=product.name,
        description=product.description,
        price=product.price,
        category=category_data,
    )

    product_doc.save()

    return f"Product {product_id} indexed successfully in Elasticsearch"


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def delete_product_from_es(self, product_id):
    try:
        product_doc = ProductDocument.get(id=product_id)
        product_doc.delete()
        return f"Product {product_id} deleted from Elasticsearch."
    except NotFoundError:
        return f"Product {product_id} not found in Elasticsearch."
    except Exception as exc:

        raise self.retry(exc=exc)
