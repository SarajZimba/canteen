# views.py
from rest_framework import viewsets
from canteen.models import PreInformedLeave
from api.serializers.student_attendancecanteen import PreInformedLeaveSerializer

class PreInformedLeaveViewSet(viewsets.ModelViewSet):
    queryset = PreInformedLeave.objects.all()
    serializer_class = PreInformedLeaveSerializer
