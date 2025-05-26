import os
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from products.models import Category


class Command(BaseCommand):
    help = 'Update categories with banner images from media/category banners folder'

    def handle(self, *args, **options):
        # Dictionary mapping category names to image filenames
        # The keys are the category names as they appear in the database (lowercase for case-insensitive matching)
        # The values are the image filenames as they appear in the media/category banners folder
        category_image_map = {
            'pickles and olives': 'Pickes & Olives.jpg',
            'sorted fruits & vegetables': 'Sorted Fruits & Vegetables.jpg',
            'frozen meat': 'Meat.jpg',  # Using Meat.jpg for Frozen Meat
            'drinks': 'Drinks.jpg',
            'nuts': 'Nuts.jpg',
            'oils and sauces': 'Oils & Sauces.jpg',
            'paking & pastry supplies': 'Paking & Pastry Supplies.jpg',
            'canned vegetables & fruits': 'Canned Vegetables and Fruits.jpg',
            'frozen food ready to cook': 'Frozen Food Ready To Cook.jpg',
            'other products': 'Other Products.jpg',
            'frozen seafood': 'Frozen Seafood.jpg',
            'poultry': 'Poultry.jpg',
            'canned legumes': 'Canned Legumes.jpg',
            'pasta': 'Pasta.jpg',
            'legumes': 'Legumes.jpg',
            'spices': 'Spices.jpg',
            'dairy derivatives & eggs': 'Dairy Derivatives and Eggs.jpg',
            'draid frutis': 'Draid Fruits.jpg',  # Note: There's a typo in the DB name 'frutis' vs 'fruits'
            'jam': 'Jam.jpg',
            'rice': 'Rice.jpg',
            'sauces': 'Sauces.jpg',
        }

        # Path to the category banners folder
        banners_dir = os.path.join('media', 'category banners')
        
        # Get all categories
        categories = Category.objects.all()
        
        # Counter for successful updates
        updated_count = 0
        
        for category in categories:
            # Get the category name (lowercase for case-insensitive matching)
            category_name = category.safe_translation_getter('name', any_language=True).lower()
            
            # Check if we have a matching image for this category
            if category_name in category_image_map:
                image_filename = category_image_map[category_name]
                image_path = os.path.join(banners_dir, image_filename)
                
                # Check if the image file exists
                if os.path.exists(image_path):
                    # Open the image file
                    with open(image_path, 'rb') as img_file:
                        # Update the category with the banner image
                        category.banner_image.save(
                            image_filename,
                            ImageFile(img_file),
                            save=True
                        )
                    
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully updated category "{category.safe_translation_getter("name", any_language=True)}" with banner image "{image_filename}"'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'Image file not found: {image_path} for category "{category.safe_translation_getter("name", any_language=True)}"'
                    ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'No matching image found for category "{category.safe_translation_getter("name", any_language=True)}"'
                ))
        
        self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} out of {categories.count()} categories with banner images'))
