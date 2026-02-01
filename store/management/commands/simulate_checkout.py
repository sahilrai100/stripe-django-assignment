from django.core.management.base import BaseCommand, CommandError
from store.models import Order
import json

class Command(BaseCommand):
    help = 'Simulate a checkout completion and create an Order (useful for demo without Stripe)'

    def add_arguments(self, parser):
        parser.add_argument('--session-id', type=str, required=True, help='Stripe session id to record')
        parser.add_argument('--amount', type=int, required=True, help='Amount in cents')
        parser.add_argument('--items', type=str, default='{}', help='JSON string for items payload')

    def handle(self, *args, **options):
        session_id = options['session_id']
        amount = options['amount']
        try:
            items = json.loads(options['items']) if options['items'] else {}
        except Exception as e:
            raise CommandError(f'Invalid JSON for --items: {e}')

        order, created = Order.objects.get_or_create(
            stripe_session_id=session_id,
            defaults={'amount': amount, 'items': items}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Order id={order.id} session={session_id} amount={amount}'))
        else:
            self.stdout.write(self.style.WARNING(f'Order already exists id={order.id} session={session_id}'))
