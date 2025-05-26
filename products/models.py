from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=100),
    )
    banner_image = models.ImageField(upload_to='category banners/', blank=True, null=True)

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)


class Product(TranslatableModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        description=models.TextField(blank=True),
    )
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)
