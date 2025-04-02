from rest_framework.viewsets import ModelViewSet

from user.models import Customer

from canteen.models import StudentAttendance

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from api.serializers.canteen import StudentAttendanceSerializer
class StudentAttendanceViewSet(ModelViewSet):
    permission_classes = [AllowAny]

    queryset = StudentAttendance.objects.filter(is_deleted= False, status=True)
    serializer_class = StudentAttendanceSerializer


from rest_framework.response import Response
class StudentAttendanceListCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        data = request.data
        # Ensure the data is always a list
        if isinstance(data, dict):  
            data = [data]
        serializer = StudentAttendanceSerializer(data=data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"Student canteen attendance created successfully"}, 200)
        else:
            return Response({"Data is not valid"}, 200)
        
class DatewiseStudentAttendanceList(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        data = request.data
        # Ensure the data is always a list
        date = data["date"]
        studentattendance_data = StudentAttendance.objects.filter(eaten_date=date)
        serializer = StudentAttendanceSerializer(studentattendance_data, many=True)

        return Response(serializer.data, 200)
    
from datetime import datetime
from django.db.models import Count
class DatewiseStudentAggregateAttendanceList(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):

        data = request.data

        # Extract 'from_date' and 'to_date' from request data
        from_date = data["from_date"]
        to_date = data["to_date"]

        # Ensure date format is correct (optional, depends on your input format)
        from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        # Query with date range filter
        meal_eatens_by_students = (
            StudentAttendance.objects
            .filter(bill_created=False, eaten_date__range=[from_date, to_date])  # Date range filter
            .values('student', 'student__name')  
            .annotate(no_of_entries=Count('id'))  
            .order_by('-no_of_entries')  
        )
        # Convert QuerySet to list for JSON response
        response_data = list(meal_eatens_by_students)
        if not response_data:
            return Response({"message": "No attendance records found for the given date range."}, status=200)
        return Response(response_data, status=200)


from canteen.utils import create_student_bills
class TestCronjob(APIView):
    def get(self, request):
        try:
            create_student_bills()
            return Response("Bill created successfully", 200)
        except Exception as e:
            return Response(str(e), 400)





