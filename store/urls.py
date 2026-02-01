from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success, name='success'),
    path('orders/', views.orders_api, name='orders_api'),
    path('webhook/', views.webhook, name='webhook'),
]
