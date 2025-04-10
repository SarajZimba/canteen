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


# class StudentCanteenAttendanceList(StudentCanteenAttendanceMixin, ListView):
#     template_name = "studentcanteenattendance/studentcanteenattendance_list.html"
#     def get_queryset(self):
#         # Query to calculate the number of meals eaten by each student
#         meal_eatens_by_students = (
#             StudentAttendance.objects
#             .filter(status=True, is_deleted=False, bill_created=False)  # Apply filters
#             .values('student', 'student__name','student__student_class', 'student__roll_no', 'student__section')  # Returns a list of dicts with student ids
#             .annotate(no_of_entries=Count('id'))  # Count entries per student
#             .order_by('-no_of_entries')  # Optional: Sort by most meals eaten
#         )
#         return meal_eatens_by_students

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Add 'meal_eatens_by_students' to context
#         context['meal_eatens_by_students'] = self.get_queryset()
#         return context

from django.db.models import Count, Sum
from django.shortcuts import render
from .models import StudentAttendance
from product.models import Product
class StudentCanteenAttendanceList(StudentCanteenAttendanceMixin, ListView):
    template_name = "studentcanteenattendance/studentcanteenattendance_list.html"

    def get_queryset(self):
        # Start with the base query
        # queryset = (
        #     StudentAttendance.objects
        #     .filter(status=True, is_deleted=False, bill_created=False)
        #     .values('student', 'student__name', 'student__student_class', 'student__roll_no', 'student__section', 'product__title', 'rate')
        #     .annotate(no_of_entries=Count('id'))
        #     .order_by('-no_of_entries')
        # )
        queryset = (
            StudentAttendance.objects
            .filter(status=True, is_deleted=False, bill_created=False)
            .values('student', 'student__name', 'student__student_class', 'student__roll_no', 'student__section')
            .annotate(no_of_entries=Count('id'), total_sum=Sum('total'))
            .order_by('-no_of_entries')
        )
        
        # If a class is provided in the GET parameters, filter by student class
        student_class = self.request.GET.get('student_class')
        if student_class:
            queryset = queryset.filter(student__student_class=student_class)

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # # Add 'meal_eatens_by_students' to context
        # context['meal_eatens_by_students'] = self.get_queryset()

        # Fetch the meal entries
        meal_eatens_by_students = list(self.get_queryset())


        # # Calculate total price for each student
        # for data in meal_eatens_by_students:
        #     no_of_dinein = data["no_of_entries"]
        #     total = no_of_dinein * data["rate"]  # Calculate total amount
        #     data["total"] = total  # Add total to context
        
        distinct_classes = StudentAttendance.objects.filter(status=True, is_deleted=False, bill_created=False) \
            .values('student__student_class') \
            .distinct()
        # Convert the queryset into the desired format (key-value pair)
        distinct_classes = [{'student__student_class': item['student__student_class']} for item in distinct_classes]

        # Remove duplicates by using a set for uniqueness
        distinct_classes = [dict(t) for t in {tuple(d.items()) for d in distinct_classes}]
        context['distinct_classes'] = distinct_classes
        context['meal_eatens_by_students'] = meal_eatens_by_students
        return context

class StudentCanteenAttendanceDetail(StudentCanteenAttendanceMixin, DetailView):
    template_name = "studentcanteenattendance/studentcanteenattendance_detail.html"


class StudentCanteenAttendanceCreate(StudentCanteenAttendanceMixin, CreateView):
    template_name = "create.html"


class StudentCanteenAttendanceUpdate(StudentCanteenAttendanceMixin, UpdateView):
    pass



class StudentCanteenAttendanceDelete(StudentCanteenAttendanceMixin, DeleteMixin, View):
    pass


from django.shortcuts import render
from bill.models import Bill

from urllib.parse import unquote

def print_multiple_bills(request, pk):
    # Decode the URL-encoded class name
    student_class = unquote(pk)
    
    # Query bills for this class
    bills = Bill.objects.filter(customer__student_class=student_class)
    
    return render(request, 'bill/studentbilldetail.html', {
        'bills': bills,
        'class_name': student_class  # Pass decoded name to template
    })

from user.models import Customer
def bill_details_view(request):
    # Query to get all bills you want to display, e.g., all bills from a certain date or status
    bills = Bill.objects.filter(customer__student_class__isnull=False)
    # Get distinct student classes and add to context
        
    # If a class is provided in the GET parameters, filter by student class
    student_class = request.GET.get('student_class')
    if student_class:
        bills = bills.filter(customer__student_class=student_class)

    distinct_classes = Customer.objects.filter(status=True, is_deleted=False, student_class__isnull=False) \
            .values('student_class') \
            .distinct()
    
        # Convert the queryset into the desired format (key-value pair)
    distinct_classes = [{'student_class': item['student_class']} for item in distinct_classes]

        # Remove duplicates by using a set for uniqueness
    distinct_classes = [dict(t) for t in {tuple(d.items()) for d in distinct_classes}]
    return render(request, 'bill/studentbilldetail.html', {'bills': bills, 'distinct_classes': distinct_classes})


import jwt
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, timezone

@login_required
def generate_login_token_and_redirect(request):
    # Use timezone-aware UTC time
    payload = {
        'user_id': request.user.id,
        'username': request.user.username,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=5),  # short expiry
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    react_login_url = f"https://attendance.houseofshoja.silverlinepos.com/auth?token={token}"
    return redirect(react_login_url)

from user.models import Customer
def single_bill_detail_view(request, pk):
    # Query to get all bills you want to display, e.g., all bills from a certain date or status
    bill = Bill.objects.get(id=pk)
    # Get distinct student classes and add to context

    return render(request, 'bill/single_studentbilldetail.html', {'bill': bill})

