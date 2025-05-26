import os
import re
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from django.conf import settings
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Import product images from media directory into the database'

    def handle(self, *args, **options):
        # Path to the products directory
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        
        if not os.path.exists(products_dir):
            self.stdout.write(self.style.ERROR(f'Directory not found: {products_dir}'))
            return
        
        # Get all category directories
        category_dirs = [d for d in os.listdir(products_dir) 
                        if os.path.isdir(os.path.join(products_dir, d))]
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(category_dirs)} categories'))
        
        # Process each category
        for category_name in category_dirs:
            # Create or get category
            category, created = Category.objects.get_or_create(
                translations__name=category_name
            )
            
            if created:
                category.set_current_language('en')
                category.name = category_name
                category.save()
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Using existing category: {category_name}'))
            
            # Get all image files in the category directory
            category_path = os.path.join(products_dir, category_name)
            image_files = [f for f in os.listdir(category_path) 
                          if os.path.isfile(os.path.join(category_path, f)) 
                          and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
                          and not f.startswith('.')]
            
            self.stdout.write(self.style.SUCCESS(f'Found {len(image_files)} images in {category_name}'))
            
            # Process each image
            for image_file in image_files:
                # Extract product name from filename (remove extension)
                product_name = os.path.splitext(image_file)[0]
                
                # Check if product already exists
                existing_product = Product.objects.filter(
                    translations__name=product_name,
                    category=category
                ).first()
                
                if existing_product:
                    self.stdout.write(self.style.WARNING(f'Product already exists: {product_name}'))
                    continue
                
                # Create new product
                product = Product()
                product.category = category
                
                # Set a default price (you can adjust this as needed)
                product.price = Decimal('0.00')
                
                # Set the product name
                product.set_current_language('en')
                product.name = product_name
                product.description = f"{product_name} in {category_name} category"
                
                # Set the image
                image_path = os.path.join(category_path, image_file)
                relative_path = os.path.relpath(image_path, settings.MEDIA_ROOT)
                
                # Save the product first to get an ID
                product.save()
                
                # Now update the image field
                with open(image_path, 'rb') as img_file:
                    product.image.save(
                        relative_path,
                        ImageFile(img_file),
                        save=True
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Created product: {product_name}'))
        
        self.stdout.write(self.style.SUCCESS('Import completed successfully'))
