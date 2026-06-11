from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from customers.views import CustomerProfileViewSet
from notifications.views import NotificationViewSet
from payments.views import (
    FavoritePaymentViewSet,
    PaymentListCreateAPIView,
    ServiceProviderViewSet,
    payment_category_detail,
    payment_category_list_create,
)
from transactions.views import (
    TopUpAPIView,
    TransactionListAPIView,
    TransferAPIView,
    WithdrawAPIView,
)
from wallets.views import BankCardViewSet, WalletViewSet

router = DefaultRouter()
router.register(r"profiles", CustomerProfileViewSet, basename="profile")
router.register(r"wallets", WalletViewSet, basename="wallet")
router.register(r"cards", BankCardViewSet, basename="card")
router.register(r"providers", ServiceProviderViewSet, basename="provider")
router.register(r"favorites", FavoritePaymentViewSet, basename="favorite")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/transactions/", TransactionListAPIView.as_view(), name="transaction-list"),
    path("api/payments/", PaymentListCreateAPIView.as_view(), name="payment-list-create"),
    path("api/top-up/", TopUpAPIView.as_view(), name="top-up"),
    path("api/transfer/", TransferAPIView.as_view(), name="transfer"),
    path("api/withdraw/", WithdrawAPIView.as_view(), name="withdraw"),
    path("api/categories/", payment_category_list_create, name="category-list-create"),
    path(
        "api/categories/<int:pk>/",
        payment_category_detail,
        name="category-detail",
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
