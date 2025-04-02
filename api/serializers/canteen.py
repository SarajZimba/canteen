# from rest_framework import serializers
# from canteen.models import StudentAttendance

# class StudentAttendanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentAttendance
#         exclude = [
#             "created_at",
#             "updated_at",
#             "status",
#             "is_deleted",
#             "sorting_order",
#             "is_featured"
#         ]

from rest_framework import serializers
from canteen.models import StudentAttendance

class StudentAttendanceSerializer(serializers.ModelSerializer):
    roll_no = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()

    class Meta:
        model = StudentAttendance
        exclude = [
            "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured"
        ]

    def get_roll_no(self, obj):
        return obj.student.roll_no if obj.student.roll_no else None
    def get_student_name(self, obj):
        return obj.student.name if obj.student.name else None
    def get_student_class(self, obj):
        return obj.student.student_class if obj.student.student_class else None
    def get_section(self, obj):
        return obj.student.section if obj.student.section else None