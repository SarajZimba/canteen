
from django.urls import path

from .views import StudentCanteenAttendanceList,StudentCanteenAttendanceDetail,StudentCanteenAttendanceCreate,StudentCanteenAttendanceUpdate,StudentCanteenAttendanceDelete
urlpatterns = [
path('studentcanteenattendance/', StudentCanteenAttendanceList.as_view(), name='studentcanteenattendance_list'),
path('studentcanteenattendance/<int:pk>/', StudentCanteenAttendanceDetail.as_view(), name='studentcanteenattendance_detail'),
path('studentcanteenattendance/create/', StudentCanteenAttendanceCreate.as_view(), name='studentcanteenattendance_create'),
path('studentcanteenattendance/<int:pk>/update/', StudentCanteenAttendanceUpdate.as_view(), name='studentcanteenattendance_update'),
path('studentcanteenattendance/delete', StudentCanteenAttendanceDelete.as_view(), name='studentcanteenattendance_delete')
]
