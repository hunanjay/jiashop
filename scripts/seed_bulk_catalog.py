"""One-off script: seed 15 product categories and 100 demo products.

Run inside the backend container (has the right DATABASE_URL):
    docker exec jiashop-backend-1 python3 scripts/seed_bulk_catalog.py

Safe to re-run: categories are upserted by name, products are skipped if a
product with the same name already exists.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from db.extensions import db
from db.models import Product, User
from services.category_service import create_category

CATEGORIES = [
    "奖牌奖杯", "文具用品", "企业礼品", "时尚配饰", "杯具水具",
    "数码科技", "家居装饰", "服装服饰", "箱包皮具", "珠宝饰品",
    "玩具乐器", "健康养生", "户外用品", "厨房用品", "图书文创",
]

PRODUCT_COUNT = 100


def seed_categories():
    for order, name in enumerate(CATEGORIES, start=1):
        create_category(name, sort_order=order, active=True)


def seed_products():
    owner = User.query.filter_by(username="admin").first()
    created = 0
    for i in range(1, PRODUCT_COUNT + 1):
        category = CATEGORIES[(i - 1) % len(CATEGORIES)]
        name = f"{category}定制礼品 {i:03d}"

        if Product.query.filter_by(name=name).first():
            continue

        product = Product(
            name=name,
            description=f"精选{category}，支持个性化定制，品质保证，适合企业采购与礼品馈赠。",
            price=round(random.uniform(19.9, 299.9), 2),
            stock=random.randint(5, 60),
            status="active",
            image_url=f"https://picsum.photos/seed/giftcraft-{i}/500/500",
            category=category,
            customization_json={"type": "Engraving", "fields": ["Name"]},
            owner_id=owner.id if owner else None,
            sales_count=random.randint(0, 500),
            is_featured=(i % 11 == 0),
            is_promotion=(i % 13 == 0),
        )
        db.session.add(product)
        created += 1

    db.session.commit()
    return created


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_categories()
        created = seed_products()
        print(f"Seed complete: {len(CATEGORIES)} categories ensured, {created} products created.")
