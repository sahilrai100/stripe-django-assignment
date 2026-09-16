from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from .models import Order

class StoreTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_orders_api_empty(self):
        resp = self.client.get(reverse('orders_api'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('orders', data)
        self.assertEqual(len(data['orders']), 0)

    @patch('store.views.stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_create):
        # mock stripe session object
        mock_create.return_value = type('S', (), {'url': 'https://example.com/session'})
        resp = self.client.post(reverse('create_checkout_session'), data='{"items": [{"id": "prod_1","quantity": 2}]}', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('url', data)
        self.assertEqual(data['url'], 'https://example.com/session')

    def test_order_model_str(self):
        o = Order.objects.create(stripe_session_id='s_1', amount=1000, items={'foo': 'bar'})
        self.assertIn('s_1', str(o))

    def test_simulate_checkout_command(self):
        from django.core.management import call_command
        call_command('simulate_checkout', '--session-id', 'sim1', '--amount', '1500', '--items', '{"items":[{"name":"T-shirt","quantity":1}]}')
        self.assertTrue(Order.objects.filter(stripe_session_id='sim1').exists())

    def test_seed_orders_command(self):
        from django.core.management import call_command
        call_command('seed_orders')
        self.assertTrue(Order.objects.filter(stripe_session_id='demo_s_1').exists())

    @patch('store.views.stripe.checkout.Session.retrieve')
    def test_unpaid_session_does_not_show_success_message(self, mock_retrieve):
        mock_retrieve.return_value = type('S', (), {
            'payment_status': 'unpaid',
            'id': 'sess_unpaid_1',
            'amount_total': 1500,
            'to_dict': lambda self: {},
        })()
        resp = self.client.get(reverse('success') + '?session_id=sess_unpaid_1')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Order.objects.filter(stripe_session_id='sess_unpaid_1').exists())
        self.assertNotIn(b'Payment successful', resp.content)

