# serializers.py
from rest_framework import serializers
from canteen.models import MonthlyAdjustments

class MonthlyAdjustmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyAdjustments
        fields = ['holiday_date', 'considered_next_month', 'month', 'year']
        read_only_fields = ['month', 'year']

    def create(self, validated_data):
        holiday_date = validated_data.get('holiday_date')
        if holiday_date:
            validated_data['month'] = holiday_date.month
            validated_data['year'] = holiday_date.year
        return MonthlyAdjustments.objects.create(**validated_data)