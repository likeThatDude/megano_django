from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path('checkout/full/<int:order_id>/', views.create_checkout_full_session, name='checkout'),
    path('checkout/one/<int:order_id>/<int:seller_id>/', views.create_checkout_current_session, name='checkout_one'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('stripe/webhook/', views.StripeWebhookAPIView.as_view(), name='stripe_webhook'),
]
