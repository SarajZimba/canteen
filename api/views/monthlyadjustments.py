from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers.monthlyadjustments import MonthlyAdjustmentsSerializer

class MonthlyAdjustmentView(APIView):
    def post(self, request, format=None):
        serializer = MonthlyAdjustmentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Holiday credit added successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)