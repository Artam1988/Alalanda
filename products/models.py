from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=100),
    )
    banner_image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)


class Product(TranslatableModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    translations = TranslatedFields(
        name=models.CharField(max_length=200, db_index=True),
    )
    image = models.ImageField(upload_to='products/')
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)
