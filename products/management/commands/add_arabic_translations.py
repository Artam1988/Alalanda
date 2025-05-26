from django.core.management.base import BaseCommand
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Add Arabic translations for existing products and categories'

    def handle(self, *args, **options):
        # Process categories
        self.stdout.write(self.style.SUCCESS('Adding Arabic translations for categories...'))
        categories = Category.objects.all()
        
        # Dictionary mapping for category translations (English to Arabic)
        category_translations = {
            "Pickles And Olives": "المخللات والزيتون",
            "Sorted Fruits & Vegetables": "الفواكه والخضروات المصنفة",
            "Frozen Meat": "اللحوم المجمدة",
            "Drinks": "المشروبات",
            "Nuts": "المكسرات",
            "Oils and Sauces": "الزيوت والصلصات",
            "Paking & Pastry Supplies": "مستلزمات التعبئة والمعجنات",
            "Canned Vegetables & Fruits": "الخضروات والفواكه المعلبة",
            "Frozen Food Ready To Cook": "الأطعمة المجمدة الجاهزة للطبخ",
            "Frozen Seafood": "المأكولات البحرية المجمدة",
            "Pasta": "المعكرونة",
            "Legumes": "البقوليات",
            "SPICES": "التوابل",
            "Dairy Derivatives & Eggs": "مشتقات الألبان والبيض",
            "Draid Frutis": "الفواكه المجففة",
            "Jam": "المربى",
            "Rice": "الأرز",
            "Sauces": "الصلصات",
            "Poultry": "الدواجن",
            "Other Products": "منتجات أخرى",
            "Canned Legumes": "البقوليات المعلبة"
        }
        
        for category in categories:
            # Get the English name
            category.set_current_language('en')
            english_name = category.name
            
            # Get Arabic translation from our dictionary
            arabic_name = category_translations.get(english_name, english_name)
            
            # Set Arabic translation
            category.set_current_language('ar')
            category.name = arabic_name
            category.save()
            
            self.stdout.write(self.style.SUCCESS(f'Added Arabic translation for category: {english_name} -> {arabic_name}'))
        
        # Process products
        self.stdout.write(self.style.SUCCESS('Adding Arabic translations for products...'))
        products = Product.objects.all()
        
        # Dictionary for common product translations
        # This is a starter set - you can expand this list as needed
        product_translations = {
            # Pickles and Olives
            "Pickeld Turnip": "مخلل لفت",
            "Pickled Cucumber": "مخلل خيار",
            "Olives Stuffed Pepper": "زيتون محشي فلفل",
            "Green Olives": "زيتون أخضر",
            "Black Olives": "زيتون أسود",
            "Mixed Pickles": "مخللات مشكلة",
            
            # Dairy products
            "Cheese": "جبنة",
            "Milk": "حليب",
            "Butter": "زبدة",
            "Egg": "بيض",
            "Labneh": "لبنة",
            
            # Meats
            "Beef": "لحم بقري",
            "Lamb": "لحم ضأن",
            "Chicken": "دجاج",
            
            # Vegetables
            "Tomato": "طماطم",
            "Potato": "بطاطس",
            "Onion": "بصل",
            "Garlic": "ثوم",
            
            # Fruits
            "Apple": "تفاح",
            "Orange": "برتقال",
            "Banana": "موز",
            
            # Nuts
            "Almond": "لوز",
            "Pistachio": "فستق",
            "Walnut": "جوز",
            "Cashew": "كاجو",
            
            # Spices
            "Salt": "ملح",
            "Pepper": "فلفل",
            "Cumin": "كمون",
            "Turmeric": "كركم",
            
            # Oils
            "Olive Oil": "زيت زيتون",
            "Sunflower Oil": "زيت عباد الشمس",
            
            # Grains
            "Rice": "أرز",
            "Wheat": "قمح",
            "Bulgur": "برغل",
            
            # Legumes
            "Beans": "فاصوليا",
            "Lentils": "عدس",
            "Chickpeas": "حمص",
            
            # Pasta
            "Spaghetti": "سباغيتي",
            "Macaroni": "معكرونة",
            
            # Sauces
            "Ketchup": "كاتشب",
            "Mayonnaise": "مايونيز",
            "Mustard": "خردل",
            "Tahini": "طحينة",
        }
        
        for product in products:
            # Get the English name and description
            product.set_current_language('en')
            english_name = product.name
            english_description = product.description or ""
            
            # Try to find a direct translation
            arabic_name = product_translations.get(english_name, None)
            
            # If no direct match, try to find partial matches
            if not arabic_name:
                for eng_term, ar_term in product_translations.items():
                    if eng_term in english_name:
                        # Replace the English term with Arabic term
                        arabic_name = english_name.replace(eng_term, ar_term)
                        break
            
            # If still no match, use the English name
            if not arabic_name:
                arabic_name = english_name
            
            # Set Arabic translation
            product.set_current_language('ar')
            product.name = arabic_name
            # Use the same description for now
            product.description = english_description
            product.save()
            
            self.stdout.write(self.style.SUCCESS(f'Added Arabic translation for product: {english_name} -> {arabic_name}'))
        
        self.stdout.write(self.style.SUCCESS('Arabic translations added successfully'))
