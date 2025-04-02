from django.shortcuts import render
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from root.utils import DeleteMixin
from .models import StudentAttendance
from .forms import StudentAttendanceForm

from user.permission import IsAdminMixin

class StudentCanteenAttendanceMixin(IsAdminMixin):
    model = StudentAttendance
    form_class = StudentAttendanceForm
    paginate_by = 50
    queryset = StudentAttendance.objects.filter(status=True, is_deleted=False)
    success_url = reverse_lazy("studentcanteenattendance_list")
    search_lookup_fields = [
        "title",
        "description",
    ]


class StudentCanteenAttendanceList(StudentCanteenAttendanceMixin, ListView):
    template_name = "studentcanteenattendance/studentcanteenattendance_list.html"
    def get_queryset(self):
        # Query to calculate the number of meals eaten by each student
        meal_eatens_by_students = (
            StudentAttendance.objects
            .filter(status=True, is_deleted=False, bill_created=False)  # Apply filters
            .values('student', 'student__name')  # Returns a list of dicts with student ids
            .annotate(no_of_entries=Count('id'))  # Count entries per student
            .order_by('-no_of_entries')  # Optional: Sort by most meals eaten
        )
        return meal_eatens_by_students

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add 'meal_eatens_by_students' to context
        context['meal_eatens_by_students'] = self.get_queryset()
        return context


# class OrderDetail(OrderMixin, DetailView):
#     template_name = "order/order_detail.html"

class StudentCanteenAttendanceDetail(StudentCanteenAttendanceMixin, DetailView):
    template_name = "studentcanteenattendance/studentcanteenattendance_detail.html"


class StudentCanteenAttendanceCreate(StudentCanteenAttendanceMixin, CreateView):
    template_name = "create.html"


class StudentCanteenAttendanceUpdate(StudentCanteenAttendanceMixin, UpdateView):
    pass



class StudentCanteenAttendanceDelete(StudentCanteenAttendanceMixin, DeleteMixin, View):
    pass