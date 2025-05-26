from django.core.management.base import BaseCommand
from products.models import Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Set all product prices to zero'

    def handle(self, *args, **options):
        # Get all products
        products = Product.objects.all()
        updated_count = 0
        
        for product in products:
            try:
                # Set price to zero
                product.price = Decimal('0.00')
                product.save()
                updated_count += 1
                
                self.stdout.write(f"Set price to 0 for '{product}'")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating price for '{product}': {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully set prices to 0 for {updated_count} products"))
