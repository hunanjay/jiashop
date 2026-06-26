"""
Fix expired OSS signed URLs stored in the database.
Scans Product.image_url, Product.images_json, Order.custom_logo_url,
Order.design_file_url, Order.effect_images_json and replaces any full
signed URLs with their bare object key (uploads/...).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from db.extensions import db
from db.models import Product, Order


def extract_key(url):
    """Return bare OSS key if url is a signed URL, else return as-is."""
    if isinstance(url, str):
        decoded = url.replace('%2F', '/')
        if '/uploads/' in decoded:
            return 'uploads/' + decoded.split('/uploads/')[1].split('?')[0]
    return url


def fix_products():
    products = Product.query.all()
    fixed = 0
    for p in products:
        changed = False

        key = extract_key(p.image_url)
        if key != p.image_url:
            p.image_url = key
            changed = True

        if p.images_json:
            new_images = [extract_key(img) for img in p.images_json]
            if new_images != p.images_json:
                p.images_json = new_images
                changed = True

        if changed:
            fixed += 1

    print(f"Products: fixed {fixed}/{len(products)}")
    return fixed


def fix_orders():
    orders = Order.query.all()
    fixed = 0
    for o in orders:
        changed = False

        key = extract_key(o.custom_logo_url)
        if key != o.custom_logo_url:
            o.custom_logo_url = key
            changed = True

        key = extract_key(o.design_file_url)
        if key != o.design_file_url:
            o.design_file_url = key
            changed = True

        if o.effect_images_json:
            new_images = [extract_key(img) for img in o.effect_images_json]
            if new_images != o.effect_images_json:
                o.effect_images_json = new_images
                changed = True

        if changed:
            fixed += 1

    print(f"Orders:   fixed {fixed}/{len(orders)}")
    return fixed


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        p = fix_products()
        o = fix_orders()
        if p + o > 0:
            db.session.commit()
            print("Done. All signed URLs replaced with object keys.")
        else:
            print("Nothing to fix.")
