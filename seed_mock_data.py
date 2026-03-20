from app import app
from seeding import seed_demo_order, seed_mock_data


if __name__ == "__main__":
    summary = seed_mock_data(app)
    seed_demo_order(app)
    print(
        "Seed complete: "
        f"{summary['roles']} roles, {summary['users']} users, {summary['products']} products"
    )
