from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Delete all products from the database.'

    def handle(self, *args, **options):
        count = Product.objects.count()
        if count == 0:
            self.stdout.write(self.style.WARNING('No products to delete.'))
            return
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} products.'))
