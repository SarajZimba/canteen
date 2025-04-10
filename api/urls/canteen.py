from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.canteen import StudentAttendanceViewSet, StudentAttendanceListCreate, DatewiseStudentAttendanceList, DatewiseStudentAggregateAttendanceList, TestCronjob, CheckoutCanteenBill, CheckoutClassBills

# Create a router and register the viewset
router = DefaultRouter()
router.register(r'studentattendance-canteen', StudentAttendanceViewSet, basename='studentattendanceapi')

urlpatterns = [
    path('create-multiple-attendance', StudentAttendanceListCreate.as_view(), name = 'create-multiple-attendance'),
    path('datefilter-canteen-attendance', DatewiseStudentAttendanceList.as_view(), name = 'datefilter-canteen-attendance'),
    path('datefilter-aggregate-canteen-attendance', DatewiseStudentAggregateAttendanceList.as_view(), name = 'datefilter-aggregate-canteen-attendance'),
    path('checkout-bill-canteen', CheckoutCanteenBill.as_view(), name = 'checkout-bill-canteen'),
    path('test-cronjob', TestCronjob.as_view(), name = 'test-cronjob'),
    path('checkout-classbills', CheckoutClassBills.as_view(), name = 'checkout-classbills'),
] + router.urls

from api.views.canteen import VerifyToken

urlpatterns += [
    path('verify-token/', VerifyToken.as_view(), name='verify-token'),
]
from api.views.canteen import StudentsServedData

urlpatterns += [
    path('served-data/', StudentsServedData.as_view(), name='served-data'),
]
