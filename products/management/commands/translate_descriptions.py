import os
import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product
from django.utils import translation

class Command(BaseCommand):
    help = 'Automatically translate product descriptions from English to Arabic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force translation even if Arabic translation already exists',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Get all products
        products = Product.objects.all()
        self.stdout.write(f"Found {products.count()} products to process")
        
        # Set up translation service (using Google Translate API)
        for product in products:
            # Get English description
            with translation.override('en'):
                english_description = product.description
                
                if not english_description:
                    self.stdout.write(self.style.WARNING(f"Product {product.id}: No English description found, skipping"))
                    continue
            
            # Check if Arabic translation already exists
            with translation.override('ar'):
                arabic_description = product.description
                
                # Skip if Arabic translation exists and not forcing
                if arabic_description and not force:
                    self.stdout.write(self.style.SUCCESS(f"Product {product.id}: Arabic translation already exists, skipping"))
                    continue
            
            # Translate the description
            try:
                translated_text = self.translate_text(english_description, 'en', 'ar')
                
                # Save the Arabic translation
                product.set_current_language('ar')
                product.description = translated_text
                product.save()
                
                self.stdout.write(self.style.SUCCESS(f"Product {product.id}: Successfully translated"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Product {product.id}: Translation failed - {str(e)}"))
    
    def translate_text(self, text, source_lang, target_lang):
        """
        Translate text using Google Translate API.
        You'll need to replace this with your preferred translation API.
        
        For demonstration, we're using a simple approach. In production,
        you should use a proper API with authentication.
        """
        # This is a simplified example using a free translation API
        # For production, consider using Google Cloud Translation API or DeepL API with proper authentication
        url = "https://translate.googleapis.com/translate_a/single"
        
        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            # Parse the response
            result = response.json()
            translated_text = ''.join([sentence[0] for sentence in result[0]])
            return translated_text
        else:
            raise Exception(f"Translation API returned status code {response.status_code}")
