from rest_framework.views import APIView

from rest_framework.response import Response

from canteen.models import WorkingDays
from rest_framework.permissions import IsAuthenticated

from api.serializers.working_days import WorkingDaysSerializer

class WorkingDaysAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        data = request.data

        serializer = WorkingDaysSerializer(data=data, many=True)

        try:
            if serializer.is_valid():
                serializer.save()   
                return Response({"data":"date has been posted"}, 200)
        except Exception as e :
            return Response({"error": str(e) }, 400)

from datetime import datetime

class HolidayAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        data = request.data  # Expecting a list of date strings
        failed_dates = []

        for datum in data:
            try:
                # Validate date format (optional but good practice)
                date_obj = datetime.strptime(datum, "%Y-%m-%d").date()
                working_day = WorkingDays.objects.filter(working_date=date_obj)
                if working_day.exists():
                    working_day.delete()
            except ValueError:
                failed_dates.append(datum)

        if failed_dates:
            return Response({"error": f"Invalid date format for: {failed_dates}"}, status=400)

        return Response({"message": "Holidays have been added"}, status=200)




        