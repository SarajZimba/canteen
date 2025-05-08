from django.urls import path
from api.views.monthlyadjustments import MonthlyAdjustmentView

urlpatterns = [
    path('monthlyadjustments-credit/', MonthlyAdjustmentView.as_view(), name='monthy-adjustments'),
]