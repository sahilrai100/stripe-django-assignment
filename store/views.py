import os
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Order
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# Fixed products
PRODUCTS = [
    {"id": "prod_1", "name": "T-shirt", "price": 1500},
    {"id": "prod_2", "name": "Mug", "price": 700},
    {"id": "prod_3", "name": "Sticker Pack", "price": 300},
]


def index(request):
    orders = Order.objects.order_by('-created_at')[:50]
    products = [{**p, 'display_price': p['price']/100.0} for p in PRODUCTS]
    return render(request, 'store/index.html', {
        'products': products,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'orders': orders,
    })


@csrf_exempt
def create_checkout_session(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    data = json.loads(request.body)
    items = data.get('items', [])
    line_items = []
    total = 0
    for it in items:
        pid = it.get('id')
        qty = int(it.get('quantity', 1))
        prod = next((p for p in PRODUCTS if p['id'] == pid), None)
        if not prod:
            continue
        unit_amount = prod['price']
        total += unit_amount * qty
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': unit_amount,
                'product_data': {'name': prod['name']},
            },
            'quantity': qty,
        })
    if not line_items:
        return JsonResponse({'error': 'no items'}, status=400)
    domain = request.build_absolute_uri('/')[:-1]
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f"{domain}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain}/",
        )
        return JsonResponse({'url': session.url})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('index')
    try:
        session = stripe.checkout.Session.retrieve(session_id, expand=['payment_intent'])
        if session.payment_status == 'paid':
            order, created = Order.objects.get_or_create(
                stripe_session_id=session.id,
                defaults={'amount': int(session.amount_total or 0), 'items': session.to_dict()},
            )
        # show success page or redirect to index with message
        orders = Order.objects.order_by('-created_at')[:50]
        return render(request, 'store/index.html', {
            'products': PRODUCTS,
            'orders': orders,
            'success_msg': 'Payment successful! Order recorded.'
        })
    except Exception:
        return redirect('index')


@csrf_exempt
def webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # idempotent create
        Order.objects.get_or_create(
            stripe_session_id=session['id'],
            defaults={'amount': session.get('amount_total', 0), 'items': session},
        )
    return HttpResponse(status=200)


def orders_api(request):
    orders = Order.objects.order_by('-created_at')[:50]
    data = [{'id': o.id, 'amount': o.amount, 'items': o.items, 'created_at': o.created_at.isoformat()} for o in orders]
    return JsonResponse({'orders': data})
