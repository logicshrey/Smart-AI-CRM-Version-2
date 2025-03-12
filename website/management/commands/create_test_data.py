from django.core.management.base import BaseCommand
from website.models import Record
from website.ai_utils import analyze_sentiment, categorize_customer, calculate_priority
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Creates test data for the CRM system'

    def handle(self, *args, **kwargs):
        # Sample data
        customers = [
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@vip-corp.com',
                'phone': '555-0101',
                'address': '123 Business Ave',
                'city': 'New York',
                'state': 'NY',
                'zipcode': '10001',
                'amount': 5000.00,
                'notes': 'Premium customer, always satisfied with our services',
                'transaction_type': 'purchase'
            },
            {
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'email': 'alice@tech-corp.com',
                'phone': '555-0102',
                'address': '456 Tech Street',
                'city': 'San Francisco',
                'state': 'CA',
                'zipcode': '94105',
                'amount': 2500.00,
                'notes': 'Having issues with the latest product, needs urgent support',
                'transaction_type': 'support'
            },
            {
                'first_name': 'Robert',
                'last_name': 'Davis',
                'email': 'robert@sales.com',
                'phone': '555-0103',
                'address': '789 Market St',
                'city': 'Chicago',
                'state': 'IL',
                'zipcode': '60601',
                'amount': 1500.00,
                'notes': 'Interested in bulk purchase, follow up needed',
                'transaction_type': 'inquiry'
            },
            {
                'first_name': 'Emma',
                'last_name': 'Wilson',
                'email': 'emma@startup.com',
                'phone': '555-0104',
                'address': '321 Innovation Rd',
                'city': 'Austin',
                'state': 'TX',
                'zipcode': '73301',
                'amount': 7500.00,
                'notes': 'New business client, very enthusiastic about partnership',
                'transaction_type': 'purchase'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Brown',
                'email': 'michael@support.com',
                'phone': '555-0105',
                'address': '654 Help Lane',
                'city': 'Boston',
                'state': 'MA',
                'zipcode': '02108',
                'amount': 100.00,
                'notes': 'Multiple complaints about service quality',
                'transaction_type': 'support'
            }
        ]

        # Create records
        for customer in customers:
            # Calculate sentiment and category
            sentiment_score = analyze_sentiment(customer['notes'])
            category = categorize_customer(customer['email'], customer['notes'])
            priority_score = calculate_priority(sentiment_score, category)

            # Create record
            record = Record.objects.create(
                first_name=customer['first_name'],
                last_name=customer['last_name'],
                email=customer['email'],
                phone=customer['phone'],
                address=customer['address'],
                city=customer['city'],
                state=customer['state'],
                zipcode=customer['zipcode'],
                amount=customer['amount'],
                transaction_type=customer['transaction_type'],
                notes=customer['notes'],
                sentiment_score=sentiment_score,
                customer_category=category,
                priority_score=priority_score
            )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created record for {customer["first_name"]} {customer["last_name"]}')
            )
