import random
from django.core.management.base import BaseCommand
from products.models import Product, Category
from decimal import Decimal

class Command(BaseCommand):
    help = 'Update product prices with suitable values in SAR'

    def handle(self, *args, **options):
        # Price ranges by category (in SAR)
        price_ranges = {
            'Canned Legumes': (5, 15),
            'Canned Vegetables & Fruits': (6, 18),
            'Dairy Derivatives & Eggs': (8, 35),
            'Draid Frutis': (15, 45),
            'Drinks': (4, 25),
            'Frozen Food Ready To Cook': (18, 45),
            'Frozen Meat': (30, 120),
            'Frozen Seafood': (25, 90),
            'Jam': (10, 25),
            'Legumes': (7, 30),
            'Nuts': (20, 80),
            'Oils and Sauces': (12, 40),
            'Pasta': (5, 20),
            'Pickles And Olives': (8, 30),
            'Poultry': (20, 60),
            'Rice': (15, 75),
            'SPICES': (6, 35),
            'Sauces': (8, 25),
            'Sorted Fruits & Vegetables': (5, 30),
            'Paking & Pastry Supplies': (10, 40),
            'Other Products': (10, 50),
        }
        
        # Default price range for any category not in our mapping
        default_range = (10, 50)
        
        # Update all products with appropriate prices
        products = Product.objects.all()
        updated_count = 0
        
        for product in products:
            try:
                category_name = product.category.safe_translation_getter('name', any_language=True)
                
                # Get price range for this category, or use default
                min_price, max_price = price_ranges.get(category_name, default_range)
                
                # Generate a random price within the range, rounded to .99 or .49
                base_price = random.uniform(min_price, max_price)
                
                # 60% chance of .99 ending, 40% chance of .49 ending
                if random.random() < 0.6:
                    price = int(base_price) + Decimal('0.99')
                else:
                    price = int(base_price) + Decimal('0.49')
                
                # Update the product price
                product.price = price
                product.save()
                updated_count += 1
                
                self.stdout.write(f"Updated price for '{product}' to {price} SAR")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating price for '{product}': {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully updated prices for {updated_count} products"))
