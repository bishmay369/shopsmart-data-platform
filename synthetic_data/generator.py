import pandas as pd
import numpy as np
from faker import Faker
import random
import uuid
import json
import os
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

# Create EXACTLY 6 folders for the 6 data sources
directories = [
    'output_data/source1_orders_pg',
    'output_data/source2_customers_api',
    'output_data/source3_products_mongo',
    'output_data/source4_clickstream_eventhub',
    'output_data/source5_inventory_csv',
    'output_data/source6_payments_api'
]
for dir_path in directories:
    os.makedirs(dir_path, exist_ok=True)

print("🛍️ Generating ShopSmart AI 6-Source Data...")

def date_to_str(d):
    return d.strftime('%Y-%m-%dT%H:%M:%SZ') if isinstance(d, datetime) else str(d)

# ---------------------------------------------------------
# SOURCE 3: Product Catalog (MongoDB / JSON)
# ---------------------------------------------------------
print("-> Generating Source 3: Products (JSON)...")
categories = ['Electronics', 'Fashion', 'Home', 'Sports', 'Beauty']
product_ids = [f"PROD{str(i).zfill(3)}" for i in range(1, 51)]
products = []

for pid in product_ids:
    price = round(random.uniform(15.0, 999.99), 2)
    products.append({
        "product_id": pid,
        "product_name": fake.catch_phrase(),
        "category": random.choice(categories),
        "sub_category": fake.word().capitalize(),
        "brand": fake.company(),
        "price": price,
        "cost_price": round(price * random.uniform(0.4, 0.7), 2),
        "weight_kg": round(random.uniform(0.1, 15.0), 2),
        "supplier_id": f"SUP{str(random.randint(1, 10)).zfill(3)}",
        "rating": round(random.uniform(2.0, 5.0), 1),
        "review_count": random.randint(0, 5000),
        "is_active": random.choice([True, True, True, False]),
        "attributes": {
            "color": [fake.color_name(), fake.color_name()],
            "battery_life": f"{random.randint(5, 40)} hours",
            "connectivity": "Bluetooth 5.0"
        },
        "created_at": date_to_str(fake.date_time_between(start_date='-2y', end_date='-1y')),
        "updated_at": date_to_str(fake.date_time_between(start_date='-1y', end_date='now'))
    })

with open('output_data/source3_products_mongo/products.json', 'w') as f:
    json.dump(products, f, indent=4)

# ---------------------------------------------------------
# SOURCE 2: Customer Data (API / JSON)
# ---------------------------------------------------------
print("-> Generating Source 2: Customers (JSON)...")
customer_ids = [f"CUST{str(i).zfill(3)}" for i in range(1, 501)]
customers = []

for cid in customer_ids:
    customers.append({
        "customer_id": cid,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email() if random.random() > 0.10 else None, # 10% dirty data
        "phone": fake.phone_number(),
        "date_of_birth": str(fake.date_of_birth(minimum_age=18, maximum_age=80)),
        "gender": random.choice(["M", "F", "O"]),
        "registration_date": str(fake.date_between(start_date='-2y', end_date='today')),
        "loyalty_tier": random.choice(["Bronze", "Silver", "Gold", "Platinum"]),
        "address": {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip": fake.zipcode(),
            "country": "US"
        },
        "preferences": {
            "categories": random.sample(categories, k=random.randint(1, 3)),
            "communication": random.sample(["email", "sms", "push"], k=random.randint(1, 2))
        }
    })

with open('output_data/source2_customers_api/customers.json', 'w') as f:
    json.dump(customers, f, indent=4)

# ---------------------------------------------------------
# SOURCE 5: Inventory Data (CSV)
# ---------------------------------------------------------
print("-> Generating Source 5: Inventory (CSV)...")
inventory = []
warehouses = ['WH001', 'WH002', 'WH003']

for pid in product_ids:
    for wh in warehouses:
        qty = random.randint(0, 1000) if random.random() > 0.05 else random.randint(-50, -1) # 5% dirty data
        inventory.append({
            "product_id": pid,
            "warehouse_id": wh,
            "quantity_on_hand": qty,
            "quantity_reserved": max(0, int(qty * random.uniform(0.0, 0.3))),
            "reorder_point": 100,
            "reorder_quantity": 250,
            "last_restock_date": fake.date_between(start_date='-3m', end_date='today'),
            "snapshot_date": datetime.now().date()
        })

pd.DataFrame(inventory).to_csv('output_data/source5_inventory_csv/inventory.csv', index=False)

# ---------------------------------------------------------
# SOURCE 1: Orders DB (PostgreSQL) & SOURCE 6: Payments (API)
# ---------------------------------------------------------
print("-> Generating Source 1 & 6: Orders and Payments...")
orders = []
order_items = []
payments = []

order_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled', 'returned']
payment_methods = ['credit_card', 'debit_card', 'upi', 'wallet', 'cod']
channels = ['web', 'mobile_app', 'in_store', 'marketplace']

for i in range(1, 2001):
    order_id = f"ORD{str(i).zfill(5)}"
    cust_id = random.choice(customer_ids)
    order_date = fake.date_time_between(start_date='-1y', end_date='now')
    status = random.choice(order_statuses) if random.random() > 0.02 else None # 2% dirty data
    
    num_items = random.randint(1, 4)
    order_total = 0
    for j in range(num_items):
        item_id = f"ITM{order_id}-{j}"
        # THE FIX: Directly pick a random product dictionary from the list
        prod = random.choice(products) 
        qty = random.randint(1, 3)
        unit_price = prod['price']
        order_total += (qty * unit_price)
        
        order_items.append({
            "item_id": item_id,
            "order_id": order_id,
            "product_id": prod['product_id'],
            "quantity": qty,
            "unit_price": unit_price,
            "discount_percent": round(random.uniform(0, 15.0), 2),
            "item_status": random.choice(['packed', 'shipped', 'delivered']),
            "created_at": date_to_str(order_date)
        })

    orders.append({
        "order_id": order_id,
        "customer_id": cust_id,
        "order_date": date_to_str(order_date),
        "order_status": status,
        "total_amount": round(order_total, 2),
        "discount_amount": round(order_total * 0.05, 2),
        "shipping_amount": 15.00 if order_total < 50 else 0.00,
        "payment_method": random.choice(payment_methods),
        "channel": random.choice(channels),
        "shipping_address_id": f"ADDR{random.randint(1, 1000)}",
        "created_at": date_to_str(order_date),
        "updated_at": date_to_str(order_date + timedelta(hours=random.randint(1, 48)))
    })

    # SOURCE 6: Payments matched to the order
    payments.append({
        "transaction_id": f"TXN{str(uuid.uuid4())[:8].upper()}",
        "order_id": order_id,
        "payment_method": random.choice(payment_methods),
        "card_type": random.choice(["visa", "mastercard", "amex", "none"]),
        "amount": round(order_total, 2),
        "currency": "USD",
        "status": "success" if status != 'cancelled' else "failed",
        "gateway_response_code": "00" if status != 'cancelled' else "05",
        "is_international": random.choice([True, False]),
        "transaction_timestamp": date_to_str(order_date + timedelta(minutes=random.randint(1, 15))),
        "risk_score": random.randint(1, 99),
        "ip_address": fake.ipv4(),
        "device_fingerprint": str(uuid.uuid4())
    })

pd.DataFrame(orders).to_csv('output_data/source1_orders_pg/orders.csv', index=False)
pd.DataFrame(order_items).to_csv('output_data/source1_orders_pg/order_items.csv', index=False)
with open('output_data/source6_payments_api/payments.json', 'w') as f:
    json.dump(payments, f, indent=4)

# ---------------------------------------------------------
# SOURCE 4: Clickstream Events (Event Hub Streaming JSON)
# ---------------------------------------------------------
print("-> Generating Source 4: Clickstream (JSONLines)...")
event_types = ['page_view', 'product_view', 'add_to_cart', 'remove_from_cart', 'checkout', 'search']
clickstream = []

for _ in range(3000):
    clickstream.append({
        "event_id": f"EVT{str(uuid.uuid4())[:10].upper()}",
        "session_id": f"SESS{random.randint(1000, 9999)}",
        "customer_id": random.choice(customer_ids) if random.random() > 0.2 else None,
        "event_type": random.choice(event_types),
        "event_timestamp": date_to_str(fake.date_time_between(start_date='-1m', end_date='now')),
        "page_url": f"/products/{random.choice(product_ids)}",
        "product_id": random.choice(product_ids),
        "device_type": random.choice(["mobile", "desktop", "tablet"]),
        "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"]),
        "os": random.choice(["Android", "iOS", "Windows", "MacOS"]),
        "ip_address": fake.ipv4(),
        "geo_location": {
            "city": fake.city(),
            "country": "US"
        },
        "referrer": random.choice(["google.com", "facebook.com", "direct", "email"]),
        "search_query": fake.word() if random.random() > 0.8 else None
    })

with open('output_data/source4_clickstream_eventhub/clickstream.json', 'w') as f:
    for event in clickstream:
        f.write(json.dumps(event) + '\n')

print("✅ Data generation complete! 6 exact sources built.")