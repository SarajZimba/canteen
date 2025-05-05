# from django.shortcuts import render
# from django.db.models import Count
# from django.urls import reverse_lazy
# from django.views.generic import (
#     CreateView,
#     DetailView,
#     ListView,
#     UpdateView,
#     View,
# )
# from root.utils import DeleteMixin
# from .models import StudentAttendance
# from .forms import StudentAttendanceForm

# from user.permission import IsAdminMixin

# class StudentCanteenAttendanceMixin(IsAdminMixin):
#     model = StudentAttendance
#     form_class = StudentAttendanceForm
#     paginate_by = 50
#     queryset = StudentAttendance.objects.filter(status=True, is_deleted=False)
#     success_url = reverse_lazy("studentcanteenattendance_list")
#     search_lookup_fields = [
#         "title",
#         "description",
#     ]


# from django.db.models import Count, Sum
# from django.shortcuts import render
# from .models import StudentAttendance
# from product.models import Product
# class StudentCanteenAttendanceList(StudentCanteenAttendanceMixin, ListView):
#     template_name = "studentcanteenattendance/studentcanteenattendance_list.html"

#     def get_queryset(self):
#         # Start with the base query
#         # queryset = (
#         #     StudentAttendance.objects
#         #     .filter(status=True, is_deleted=False, bill_created=False)
#         #     .values('student', 'student__name', 'student__student_class', 'student__roll_no', 'student__section', 'product__title', 'rate')
#         #     .annotate(no_of_entries=Count('id'))
#         #     .order_by('-no_of_entries')
#         # )
#         queryset = (
#             StudentAttendance.objects
#             .filter(status=True, is_deleted=False, bill_created=False)
#             .values('student', 'student__name', 'student__student_class', 'student__roll_no', 'student__section')
#             .annotate(no_of_entries=Count('id'), total_sum=Sum('total'))
#             .order_by('-no_of_entries')
#         )
        
#         # If a class is provided in the GET parameters, filter by student class
#         student_class = self.request.GET.get('student_class')
#         if student_class:
#             queryset = queryset.filter(student__student_class=student_class)

#         return queryset


#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # # Add 'meal_eatens_by_students' to context
#         # context['meal_eatens_by_students'] = self.get_queryset()

#         # Fetch the meal entries
#         meal_eatens_by_students = list(self.get_queryset())


#         # # Calculate total price for each student
#         # for data in meal_eatens_by_students:
#         #     no_of_dinein = data["no_of_entries"]
#         #     total = no_of_dinein * data["rate"]  # Calculate total amount
#         #     data["total"] = total  # Add total to context
        
#         # distinct_classes = StudentAttendance.objects.filter(status=True, is_deleted=False, bill_created=False) \
#         #     .values('student__student_class') \
#         #     .distinct()
#         distinct_classes = Customer.objects.filter(status=True, is_deleted=False) \
#             .values('student_class') \
#             .distinct()
#         # Convert the queryset into the desired format (key-value pair)
#         distinct_classes = [{'student__student_class': item['student_class']} for item in distinct_classes]

#         # Remove duplicates by using a set for uniqueness
#         distinct_classes = [dict(t) for t in {tuple(d.items()) for d in distinct_classes}]
#         context['distinct_classes'] = distinct_classes
#         context['meal_eatens_by_students'] = meal_eatens_by_students
#         return context

# class StudentCanteenAttendanceDetail(StudentCanteenAttendanceMixin, DetailView):
#     template_name = "studentcanteenattendance/studentcanteenattendance_detail.html"


# class StudentCanteenAttendanceCreate(StudentCanteenAttendanceMixin, CreateView):
#     template_name = "create.html"


# class StudentCanteenAttendanceUpdate(StudentCanteenAttendanceMixin, UpdateView):
#     pass



# class StudentCanteenAttendanceDelete(StudentCanteenAttendanceMixin, DeleteMixin, View):
#     pass


# from django.shortcuts import render
# from bill.models import Bill

# from urllib.parse import unquote

# def print_multiple_bills(request, pk):
#     # Decode the URL-encoded class name
#     student_class = unquote(pk)
    
#     # Query bills for this class
#     bills = Bill.objects.filter(customer__student_class=student_class)
    
#     return render(request, 'bill/studentbilldetail.html', {
#         'bills': bills,
#         'class_name': student_class  # Pass decoded name to template
#     })

# from user.models import Customer
# def bill_details_view(request):
#     # Query to get all bills you want to display, e.g., all bills from a certain date or status
#     bills = Bill.objects.filter(customer__student_class__isnull=False)
#     # Get distinct student classes and add to context
        
#     # If a class is provided in the GET parameters, filter by student class
#     student_class = request.GET.get('student_class')
#     if student_class:
#         bills = bills.filter(customer__student_class=student_class)

#     distinct_classes = Customer.objects.filter(status=True, is_deleted=False, student_class__isnull=False) \
#             .values('student_class') \
#             .distinct()
    
#         # Convert the queryset into the desired format (key-value pair)
#     distinct_classes = [{'student_class': item['student_class']} for item in distinct_classes]

#         # Remove duplicates by using a set for uniqueness
#     distinct_classes = [dict(t) for t in {tuple(d.items()) for d in distinct_classes}]
#     return render(request, 'bill/studentbilldetail.html', {'bills': bills, 'distinct_classes': distinct_classes})


# import jwt
# from django.conf import settings
# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required
# from datetime import datetime, timedelta, timezone

# @login_required
# def generate_login_token_and_redirect(request):
#     # Use timezone-aware UTC time
#     payload = {
#         'user_id': request.user.id,
#         'username': request.user.username,
#         'exp': datetime.now(timezone.utc) + timedelta(minutes=5),  # short expiry
#     }
#     token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

#     react_login_url = f"https://attendance.houseofshoja.silverlinepos.com/auth?token={token}"
#     return redirect(react_login_url)

# from user.models import Customer
# def single_bill_detail_view(request, pk):
#     # Query to get all bills you want to display, e.g., all bills from a certain date or status
#     bill = Bill.objects.get(id=pk)
#     # Get distinct student classes and add to context

#     return render(request, 'bill/single_studentbilldetail.html', {'bill': bill})



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

# from django.db.models import Count, Sum
# from django.shortcuts import render
# from .models import StudentAttendance
# from product.models import Product
# class StudentCanteenAttendanceList(StudentCanteenAttendanceMixin, ListView):
#     template_name = "studentcanteenattendance/studentcanteenattendance_list.html"

#     def get_queryset(self):
#         queryset = (
#             StudentAttendance.objects
#             .filter(status=True, is_deleted=False, bill_created=False)
#             .values('student', 'student__name', 'student__student_class', 'student__roll_no', 'student__section')
#             .annotate(no_of_entries=Count('id'), total_sum=Sum('total'))
#             .order_by('-no_of_entries')
#         )
        
#         # If a class is provided in the GET parameters, filter by student class
#         student_class = self.request.GET.get('student_class')
#         if student_class:
#             queryset = queryset.filter(student__student_class=student_class)

#         return queryset


#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # # Add 'meal_eatens_by_students' to context
#         # context['meal_eatens_by_students'] = self.get_queryset()

#         # Fetch the meal entries
#         meal_eatens_by_students = list(self.get_queryset())
        
#         distinct_classes = StudentAttendance.objects.filter(status=True, is_deleted=False, bill_created=False) \
#             .values('student__student_class') \
#             .distinct()
#         # Convert the queryset into the desired format (key-value pair)
#         distinct_classes = [{'student__student_class': item['student__student_class']} for item in distinct_classes]

#         # Remove duplicates by using a set for uniqueness
#         distinct_classes = [dict(t) for t in {tuple(d.items()) for d in distinct_classes}]
#         context['distinct_classes'] = distinct_classes
#         context['meal_eatens_by_students'] = meal_eatens_by_students
#         return context

from django.db.models import Count, Sum
from django.shortcuts import render
from .models import StudentAttendance
from product.models import Product
class StudentCanteenAttendanceList(StudentCanteenAttendanceMixin, ListView):
    template_name = "studentcanteenattendance/studentcanteenattendance_list.html"

    def get_queryset(self):
        # Start with the base query
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

        # Fetch the meal entries
        meal_eatens_by_students = list(self.get_queryset())

        distinct_classes = Customer.objects.filter(status=True, is_deleted=False) \
            .values('student_class') \
            .distinct()
        # Convert the queryset into the desired format (key-value pair)
        distinct_classes = [{'student__student_class': item['student_class']} for item in distinct_classes]

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

    # Now calculate total_quantity and total_amount per bill
    for bill in bills:
        total_quantity = sum(item.product_quantity for item in bill.bill_items.all())
        total_amount = sum(item.amount for item in bill.bill_items.all())
        bill.total_quantity = total_quantity
        bill.total_amount = total_amount
    
    return render(request, 'bill/studentbilldetail.html', {
        'bills': bills,
        'class_name': student_class  # Pass decoded name to template
    })

# from user.models import Customer
# def bill_details_view(request):
#     # Query to get all bills you want to display, e.g., all bills from a certain date or status
#     # bills = Bill.objects.filter(customer__student_class__isnull=False)
#     bills = []
#     # Get distinct student classes and add to context
        
#     # If a class is provided in the GET parameters, filter by student class
#     student_class = request.GET.get('student_class')
#     if student_class:
#         bills = Bill.objects.filter(customer__student_class=student_class)
#     distinct_classes = Customer.objects.filter(status=True, is_deleted=False, student_class__isnull=False) \
#             .values('student_class') \
#             .distinct()
    
#         # Convert the queryset into the desired format (key-value pair)
#     distinct_classes = [{'student_class': item['student_class']} for item in distinct_classes]

#         # Remove duplicates by using a set for uniqueness
#     distinct_classes = [dict(t) for t in {tuple(d.items()) for d in distinct_classes}]

#     # Now calculate total_quantity and total_amount per bill
#     for bill in bills:
#         total_quantity = sum(item.product_quantity for item in bill.bill_items.all())
#         total_amount = sum(item.amount for item in bill.bill_items.all())
#         bill.total_quantity = total_quantity
#         bill.total_amount = total_amount


#     return render(request, 'bill/studentbilldetail.html', {'bills': bills, 'distinct_classes': distinct_classes})


# from django.db.models import Count
# from user.models import Customer

# def bill_details_view(request):
#     # Get filter parameters
#     student_class = request.GET.get('student_class')
#     student_section = request.GET.get('student_section')
    
#     # Start with base queryset
#     bills = Bill.objects.all()
    
#     # Apply filters if provided
#     if student_class:
#         bills = bills.filter(customer__student_class=student_class)
#     if student_section:
#         bills = bills.filter(customer__section=student_section)
    
#     # Get distinct classes for dropdown
#     distinct_classes = Customer.objects.filter(
#         status=True, 
#         is_deleted=False, 
#         student_class__isnull=False
#     ).values('student_class').distinct()
    
#     # Convert to desired format
#     distinct_classes = [{'student_class': item['student_class']} for item in distinct_classes]
#     distinct_classes = [dict(t) for t in {tuple(d.items()) for d in distinct_classes}]
    
#     # Get sections for the selected class (if any)
#     sections_for_class = []
#     if student_class:
#         sections_for_class = Customer.objects.filter(
#             student_class=student_class,
#             section__isnull=False
#         ).exclude(section__exact='').values_list('section', flat=True).distinct()
    
#     # Calculate totals
#     for bill in bills:
#         bill.total_quantity = sum(item.product_quantity for item in bill.bill_items.all())
#         bill.total_amount = sum(item.amount for item in bill.bill_items.all())
    
#     return render(request, 'bill/studentbilldetail.html', {
#         'bills': bills,
#         'distinct_classes': distinct_classes,
#         'sections_for_class': sections_for_class
#     })


# from django.db.models import Count
# from user.models import Customer
# from django.http import JsonResponse

# def bill_details_view(request):
#     # Get filter parameters
#     student_class = request.GET.get('student_class')
#     student_section = request.GET.get('student_section')
    
#     # Get distinct classes for dropdown (always needed)
#     distinct_classes = Customer.objects.filter(
#         status=True, 
#         is_deleted=False, 
#         student_class__isnull=False
#     ).values('student_class').distinct()
    
#     # Convert to desired format
#     distinct_classes = [{'student_class': item['student_class']} for item in distinct_classes]
#     distinct_classes = [dict(t) for t in {tuple(d.items()) for d in distinct_classes}]
    
#     # Initialize bills as empty queryset
#     bills = Bill.objects.none()
    
#     # Only query bills if BOTH filters are provided
#     if student_class and student_section:
#         bills = Bill.objects.filter(
#             customer__student_class=student_class,
#             customer__section=student_section
#         )
        
#         # Calculate totals
#         for bill in bills:
#             bill.total_quantity = sum(item.product_quantity for item in bill.bill_items.all())
#             bill.total_amount = sum(item.amount for item in bill.bill_items.all())
    
#     # Get sections for the selected class (if any)
#     sections_for_class = []
#     if student_class:
#         sections_for_class = Customer.objects.filter(
#             student_class=student_class,
#             section__isnull=False
#         ).exclude(section__exact='').values_list('section', flat=True).distinct()
    
#     # For AJAX requests (section dropdown)
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return JsonResponse({
#             'sections': list(sections_for_class),
#             'current_section': request.GET.get('student_section', '')
#         })
    
#     return render(request, 'bill/studentbilldetail.html', {
#         'bills': bills,
#         'distinct_classes': distinct_classes,
#         'sections_for_class': sections_for_class
#     })

from django.db.models import Count, Q
from user.models import Customer
from django.http import JsonResponse

def bill_details_view(request):
    # Get filter parameters
    student_class = request.GET.get('student_class')
    student_section = request.GET.get('student_section')
    student_name = request.GET.get('student_name')
    
    # Get distinct classes for dropdown (always needed)
    distinct_classes = Customer.objects.filter(
        status=True, 
        is_deleted=False, 
        student_class__isnull=False
    ).values('student_class').distinct()
    
    # Convert to desired format
    distinct_classes = [{'student_class': item['student_class']} for item in distinct_classes]
    distinct_classes = [dict(t) for t in {tuple(d.items()) for d in distinct_classes}]
    
    # Initialize bills as empty queryset
    bills = Bill.objects.none()
    
    # Build filter conditions
    filters = Q()
    
    if student_class:
        filters &= Q(customer__student_class=student_class)
    if student_section:
        filters &= Q(customer__section=student_section)
    if student_name:
        filters &= Q(customer__name__icontains=student_name)
    
    # Only query bills if at least one filter is provided
    if student_class or student_section or student_name:
        bills = Bill.objects.filter(filters)
        
        # Calculate totals
        for bill in bills:
            bill.total_quantity = sum(item.product_quantity for item in bill.bill_items.all())
            bill.total_amount = sum(item.amount for item in bill.bill_items.all())
    
    # Get sections for the selected class (if any)
    sections_for_class = []
    if student_class:
        sections_for_class = Customer.objects.filter(
            student_class=student_class,
            section__isnull=False
        ).exclude(section__exact='').values_list('section', flat=True).distinct()
    
    # For AJAX requests (section dropdown)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'sections': list(sections_for_class),
            'current_section': request.GET.get('student_section', '')
        })
    
    return render(request, 'bill/studentbilldetail.html', {
        'bills': bills,
        'distinct_classes': distinct_classes,
        'sections_for_class': sections_for_class
    })


import jwt
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, timezone
from rest_framework_simplejwt.tokens import AccessToken
@login_required
def generate_login_token_and_redirect(request):
    # Use timezone-aware UTC time
    # payload = {
    #     'user_id': request.user.id,
    #     'username': request.user.username,
    #     'exp': datetime.now(timezone.utc) + timedelta(minutes=5),  # short expiry
    # }
    # token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    # react_login_url = f"https://attendance.houseofshuboja.silverlinepos.com/auth?token={token}"
    # return redirect(react_login_url)
    token = AccessToken.for_user(request.user)
    # Optional: set custom expiry time (e.g., 5 minutes)
    token.set_exp(from_time=datetime.now(timezone.utc) + timedelta(minutes=5))

    react_login_url = f"https://attendance.houseofshuboja.silverlinepos.com/auth?token={str(token)}"
    return redirect(react_login_url)

def single_bill_detail_view(request, pk):
    # Query to get all bills you want to display, e.g., all bills from a certain date or status
    bill = Bill.objects.get(id=pk)
    # Get distinct student classes and add to context

    return render(request, 'bill/single_studentbilldetail.html', {'bill': bill})
