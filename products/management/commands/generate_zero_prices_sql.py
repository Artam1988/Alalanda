from django.core.management.base import BaseCommand
from products.models import Product
import os

class Command(BaseCommand):
    help = 'Generate SQL to set all product prices to zero'

    def handle(self, *args, **options):
        # Get all products
        products = Product.objects.all()
        product_count = 0
        
        # Create SQL file
        sql_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'set_zero_prices.sql')
        
        with open(sql_file_path, 'w') as sql_file:
            sql_file.write("-- SQL to set all product prices to zero\n\n")
            sql_file.write("BEGIN;\n\n")
            
            for product in products:
                try:
                    # Generate SQL to update price
                    sql = f"UPDATE products_product SET price = 0.00 WHERE id = {product.id};\n"
                    sql_file.write(sql)
                    product_count += 1
                    
                    self.stdout.write(f"Generated SQL for '{product}'")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error generating SQL for '{product}': {e}"))
            
            sql_file.write("\nCOMMIT;\n")
        
        self.stdout.write(self.style.SUCCESS(f"Successfully generated SQL for {product_count} products"))
        self.stdout.write(self.style.SUCCESS(f"SQL file created at: {sql_file_path}"))
