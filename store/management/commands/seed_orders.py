from django.core.management.base import BaseCommand
from store.models import Order

class Command(BaseCommand):
    help = 'Seed the database with example paid orders for demo'

    def handle(self, *args, **options):
        examples = [
            ('demo_s_1', 2500, {'items': [{'name': 'T-shirt', 'quantity': 1}]}),
            ('demo_s_2', 700, {'items': [{'name': 'Mug', 'quantity': 1}]}),
        ]
        for sid, amount, items in examples:
            order, created = Order.objects.get_or_create(stripe_session_id=sid, defaults={'amount': amount, 'items': items})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {order}'))
            else:
                self.stdout.write(self.style.WARNING(f'Exists {order}'))
