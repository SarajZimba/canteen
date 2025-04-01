from django.urls import path
from api.views.purchase import CreatePurchaseAPIView, DeletePurchaseAPIView



urlpatterns = [
    path('purchase-create/', CreatePurchaseAPIView.as_view(), name='purchase-create-api'),
    path('purchase-delete/', DeletePurchaseAPIView.as_view(), name='purchase-delete-api'),

]
