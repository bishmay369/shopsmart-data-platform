# ============================================================
# stream_producer.py
# ============================================================
# PURPOSE:
#   Simulates real-time clickstream events from an e-commerce
#   website and sends them to Azure Event Hub.
#
# HOW IT WORKS:
#   1. Generates a fake clickstream event (page view, add to
#      cart, checkout, etc.) every 1-2 seconds
#   2. Sends each event as JSON to Azure Event Hub
#   3. Runs continuously until you press Ctrl+C
#
# IN YOUR ARCHITECTURE:
#   This script simulates the "Clickstream (MongoDB)" and
#   "Store Sensors (IoT)" data sources sending real-time
#   events to the "Azure Event Hubs" ingestion layer.
#
# USAGE:
#   python stream_producer.py
#   (Press Ctrl+C to stop)
# ============================================================

from azure.eventhub import EventHubProducerClient, EventData
import json
import random
import time
import uuid
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
# Replace with your actual connection string

import os

EVENTHUB_NAME = os.environ.get("EVENTHUB_NAME", "eh-clickstream")
CONNECTION_STR = os.environ.get("EVENTHUB_CONNECTION_STRING")

if not CONNECTION_STR:
    raise ValueError("Missing EVENTHUB_CONNECTION_STRING environment variable")


# ============================================================
# DATA GENERATORS
# ============================================================
# These match the same IDs from your Bronze data
# so the streaming data can JOIN with existing Silver tables

CUSTOMER_IDS = ["CUST" + str(i).zfill(3) for i in range(1, 501)]
PRODUCT_IDS = ["PROD" + str(i).zfill(3) for i in range(1, 51)]

EVENT_TYPES = [
    "page_view",        # User opens a page
    "product_view",     # User looks at a product
    "add_to_cart",      # User adds item to cart
    "remove_from_cart", # User removes item from cart
    "checkout",         # User completes purchase
    "search",           # User searches for something
    "wishlist_add",     # User saves item for later
]

# Weights: page_view happens most, checkout least (realistic funnel)
EVENT_WEIGHTS = [30, 25, 15, 5, 8, 12, 5]

DEVICE_TYPES = ["mobile", "desktop", "tablet"]
DEVICE_WEIGHTS = [50, 35, 15]

BROWSERS = ["Chrome", "Safari", "Firefox", "Edge"]
OS_LIST = ["Android", "iOS", "Windows", "MacOS"]
REFERRERS = ["google.com", "facebook.com", "instagram.com", "direct", "email", "twitter.com"]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Seattle", "Denver", "Boston", "Miami", "Austin",
    "San Francisco", "Portland", "Nashville", "Atlanta", "Dallas"
]

SEARCH_QUERIES = [
    "bluetooth headphones", "running shoes", "laptop stand",
    "yoga mat", "phone case", "water bottle", "backpack",
    "wireless mouse", "desk lamp", "coffee maker",
    "smart watch", "air purifier", "gaming keyboard",
    None, None, None, None, None  # Most events have no search
]


def generate_event():
    """Generate a single realistic clickstream event"""

    # 20% of events are anonymous (not logged in) - matches your data
    customer_id = random.choice(CUSTOMER_IDS) if random.random() > 0.2 else None
    event_type = random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS, k=1)[0]
    product_id = random.choice(PRODUCT_IDS)
    device = random.choices(DEVICE_TYPES, weights=DEVICE_WEIGHTS, k=1)[0]

    event = {
        "event_id": "EVT-" + uuid.uuid4().hex[:12].upper(),
        "session_id": "SESS" + str(random.randint(10000, 99999)),
        "customer_id": customer_id,
        "event_type": event_type,
        "event_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "page_url": "/products/" + product_id,
        "product_id": product_id,
        "device_type": device,
        "browser": random.choice(BROWSERS),
        "os": random.choice(OS_LIST),
        "ip_address": ".".join(str(random.randint(1, 255)) for _ in range(4)),
        "geo_location": {
            "city": random.choice(CITIES),
            "country": "US"
        },
        "referrer": random.choice(REFERRERS),
        "search_query": random.choice(SEARCH_QUERIES),
        # Extra fields for richer analytics
        "page_load_time_ms": random.randint(100, 5000),
        "time_on_page_sec": random.randint(1, 300),
        "scroll_depth_pct": random.randint(0, 100),
    }

    return event


def send_events(num_events=100, delay_seconds=1):
    """Send events to Event Hub"""

    print("=" * 60)
    print("SHOPSMART AI - STREAMING PRODUCER")
    print("=" * 60)
    print("  Event Hub:  " + EVENTHUB_NAME)
    print("  Namespace:  ehns-shopsmart-dev-123")
    print("  Events:     " + str(num_events))
    print("  Delay:      " + str(delay_seconds) + " seconds between events")
    print("=" * 60)

    # Create producer client
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENTHUB_NAME
    )

    sent_count = 0
    event_type_counts = {}

    try:
        print("\nSending events... (Press Ctrl+C to stop)\n")

        for i in range(num_events):
            # Generate event
            event = generate_event()
            event_json = json.dumps(event)

            # Create batch and send
            event_data_batch = producer.create_batch()
            event_data_batch.add(EventData(event_json))
            producer.send_batch(event_data_batch)

            sent_count += 1

            # Track event types
            et = event["event_type"]
            event_type_counts[et] = event_type_counts.get(et, 0) + 1

            # Print progress
            customer_display = event["customer_id"] if event["customer_id"] else "ANONYMOUS"
            print("  [" + str(sent_count).rjust(4) + "/" + str(num_events) + "] "
                  + event["event_type"].ljust(18)
                  + customer_display.ljust(12)
                  + event["product_id"] + "  "
                  + event["device_type"])

            # Wait before sending next event
            time.sleep(delay_seconds)

    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    finally:
        producer.close()

    # Print summary
    print("\n" + "=" * 60)
    print("STREAMING SUMMARY")
    print("=" * 60)
    print("  Total events sent: " + str(sent_count))
    print("\n  Events by type:")
    for et, count in sorted(event_type_counts.items(), key=lambda x: -x[1]):
        print("    " + et.ljust(20) + str(count))
    print("\nDone! Events are now in Event Hub, ready for Databricks to consume.")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    # Send 50 events with 1 second delay (takes ~1 minute)
    # Change num_events to send more, delay_seconds for speed
    send_events(num_events=50, delay_seconds=1)