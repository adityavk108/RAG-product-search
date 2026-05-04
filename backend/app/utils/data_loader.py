import pandas as pd
from pathlib import Path
from typing import List
from PIL import Image
from app.models.product import ProductBase


def load_products_from_csv(csv_path: str) -> List[ProductBase]:
    """Load products from CSV file and return list of ProductBase objects."""
    # Read with proper handling for embedded commas in fields
    df = pd.read_csv(
        csv_path, 
        quotechar='"', 
        on_bad_lines='skip'
    )
    
    # Print columns for debugging
    print(f"CSV columns: {df.columns.tolist()}")
    print(f"Total rows: {len(df)}")
    
    # Handle potential column name issues
    # Expected columns: product_id, name, description, brand, category, price, image_file, rating, reviews
    
    products = []
    for idx, row in df.iterrows():
        try:
            # Handle missing optional fields
            reviews = []
            if 'reviews' in row and pd.notna(row.get('reviews')):
                reviews = str(row['reviews']).split(';')
                reviews = [r.strip() for r in reviews if r.strip()]

            # Get values, handle missing
            product_id = str(row.get('product_id', f'P{idx:03d}'))
            name = str(row.get('name', 'Unknown'))
            description = str(row.get('description', ''))
            brand = str(row.get('brand', 'Unknown'))
            category = str(row.get('category', 'General'))
            
            # Handle price - might be string with commas
            price_str = str(row.get('price', '0'))
            try:
                price = float(price_str.replace(',', ''))
            except:
                price = 0.0
                
            image_path = str(row.get('image_file', ''))
            
            # Handle rating
            rating = None
            if pd.notna(row.get('rating')):
                try:
                    rating = float(row.get('rating'))
                except:
                    rating = None

            product = ProductBase(
                product_id=product_id,
                name=name,
                description=description,
                brand=brand,
                category=category,
                price=price,
                image_path=image_path,
                rating=rating,
                reviews=reviews
            )
            products.append(product)
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue

    return products


def load_image(image_path: str) -> Image.Image:
    """Load and return a PIL Image from the given path."""
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return img


def get_product_text(product: ProductBase) -> str:
    """Combine product fields into a single text string for embedding."""
    return f"Name: {product.name}. Description: {product.description}. Brand: {product.brand}, Category: {product.category}"


def get_csv_path() -> Path:
    """Get the path to the products CSV file."""
    return Path("/app/data/products.csv")


def get_images_dir() -> Path:
    """Get the path to the images directory."""
    return Path("/app/data/images")