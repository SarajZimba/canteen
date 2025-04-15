from rest_framework.views import APIView

from rest_framework.response import Response

from canteen.models import WorkingDays

from api.serializers.working_days import WorkingDaysSerializer

class WorkingDaysAPI(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        serializer = WorkingDaysSerializer(data=data, many=True)

        try:
            if serializer.is_valid():
                serializer.save()   
                return Response({"data":"date has been posted"}, 200)
        except Exception as e :
            return Response({"error": str(e) }, 400)

        