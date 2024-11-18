from django.urls import path

from . import views

app_name = "payment"

urlpatterns = [
    path("checkout/full/<int:order_id>/", views.CreateCheckoutView.as_view(), name="checkout"),
    path("checkout/one/order-<int:order_id>/seller-<int:seller_id>/",
         views.CreateCheckoutCurrentView.as_view(), name="checkout_one"),
    path("payment-success/", views.PaymentSuccessView.as_view(), name="payment_success"),
    path("payment-cancel/", views.PaymentCuncelView.as_view(), name="payment_cancel"),
    path("stripe/webhook/", views.StripeWebhookAPIView.as_view(), name="stripe_webhook"),
]
