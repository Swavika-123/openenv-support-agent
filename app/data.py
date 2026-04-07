from typing import Dict, List, Any

# Mock Ticket Database
TICKETS = {
    "T-101": {
        "id": "T-101",
        "customer_id": "C-001",
        "email": "customer1@example.com",
        "subject": "Refund Request",
        "message": "Hi, I purchased the 'Deluxe' subscription 15 days ago but I've decided it's not for me. Can I get a refund?",
        "status": "Open",
        "priority": "Medium",
        "history": []
    },
    "T-102": {
        "id": "T-102",
        "customer_id": "C-002",
        "email": "customer2@example.com",
        "subject": "Login Error",
        "message": "Hello, I get a '500 Server Error' when I try to log in to my account. Please help!",
        "status": "Open",
        "priority": "High",
        "history": []
    },
    "T-103": {
        "id": "T-103",
        "customer_id": "C-003",
        "email": "customer3@example.com",
        "subject": "Missing Item",
        "message": "I ordered 3 books but only received 2. This is unacceptable!!",
        "status": "Open",
        "priority": "High",
        "history": []
    },
    "T-104": {
        "id": "T-104",
        "customer_id": "C-003", # Same customer as T-103
        "email": "customer3@example.com",
        "subject": "Order #4567 incomplete",
        "message": "I'm still waiting for my missing book. Where is it!?",
        "status": "Open",
        "priority": "High",
        "history": []
    }
}

# Mock CRM Database
CUSTOMERS = {
    "C-001": {
        "name": "Jane Doe",
        "email": "customer1@example.com",
        "subscription": "Deluxe",
        "purchase_date": "2026-03-22",
        "refund_policy": "30 days money-back guarantee",
        "total_spend": 299.99
    },
    "C-002": {
        "name": "Bob Smith",
        "email": "customer2@example.com",
        "subscription": "Free",
        "purchase_date": None,
        "history": [
            {"date": "2026-01-10", "event": "Login error", "resolution": "Advised to clear cache - resolved."}
        ]
    },
    "C-003": {
        "name": "Angry Alice",
        "email": "customer3@example.com",
        "subscription": "Gold",
        "purchase_date": "2026-04-01",
        "order_history": [
            {"order_id": "4567", "items": ["Book A", "Book B", "Book C"], "status": "Shipped"}
        ]
    }
}
