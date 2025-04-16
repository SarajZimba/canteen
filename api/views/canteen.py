from rest_framework.viewsets import ModelViewSet

from user.models import Customer

from canteen.models import StudentAttendance

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from rest_framework.permissions import IsAuthenticated

from api.serializers.canteen import StudentAttendanceSerializer
class StudentAttendanceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = StudentAttendance.objects.filter(is_deleted= False, status=True)
    serializer_class = StudentAttendanceSerializer

    # def delete(self, request, *args, **kwargs):
    def destroy(self, request, *args, **kwargs):
        # Retrieve the object to be deleted
        student_attendance = self.get_object()

        # Check if the attendance record is associated with a bill
        if student_attendance.bill_created == True:
            return Response(
                {"detail": "Cannot delete attendance because a bill exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If no bill exists, proceed with deletion
        return super().destroy(request, *args, **kwargs)




from rest_framework.response import Response
from django.db import transaction
from datetime import datetime
from canteen.utils import check_studentattendance_forleave
from canteen.models import tblmissedattendance

class StudentAttendanceListCreate(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        json_data = request.data
        # data = request.data

        data = json_data.get('present', None)

        absent_data = json_data.get('absent', None)


        # Ensure the data is always a list
        if isinstance(data, dict):  
            data = [data]
        if data != []:
            student_class = data[0]["class"]   
        
        for entry in data:
            # Check if the attendance entry for the student already exists for the given date
            student_id = entry.get("student")
            eaten_date = entry.get("eaten_date")

            # Check if an attendance record already exists for this student and eaten_date
            existing_entry = StudentAttendance.objects.filter(student=student_id, eaten_date=eaten_date).first()
                
            if existing_entry:
                return Response(
                        {"error": f"Attendance for student {existing_entry.student.name} on {eaten_date} already exists."},
                        status=400
                )
            
            else:
                tblmissedattendance_obj = tblmissedattendance.objects.filter(student__id = student_id, missed_date=eaten_date).first()
                if tblmissedattendance_obj:
                    tblmissedattendance_obj.delete()

        # today_day = datetime.today().strftime("%A")  # e.g., "Monday"  
        # today_day = "Wednesday"  # e.g., "Monday"  

        veg_canteen_product = Product.objects.filter(is_canteen_item=True, lunch_type="veg").first()
        veg_product_rate = veg_canteen_product.price if veg_canteen_product else 0.0

        nonveg_canteen_product = Product.objects.filter(is_canteen_item=True, lunch_type="nonveg").first()
        nonveg_product_rate = nonveg_canteen_product.price if nonveg_canteen_product else 0.0

        egg_canteen_product = Product.objects.filter(is_canteen_item=True, lunch_type="egg").first()
        egg_product_rate = egg_canteen_product.price if egg_canteen_product else 0.0


        for datum in data:
            eaten_date_str = datum.get("eaten_date")

            # Convert eaten_date string to day of the week
            today_day = datetime.strptime(eaten_date_str, "%Y-%m-%d").strftime("%A")
            if today_day == "Wednesday":   
                student = Customer.objects.filter(id=datum["student"]).first()
                if student:
                    student_meal_preference = student.meal_preference

                    if student_meal_preference == "nonveg":
                        datum["product"] = nonveg_canteen_product.id
                        datum["rate"] = nonveg_product_rate
                        datum["total"] = nonveg_product_rate
                    else:
                        datum["product"] = veg_canteen_product.id
                        datum["rate"] = veg_product_rate
                        datum["total"] = veg_product_rate
                else:
                    print("Student id came null for wednesday meal preference")

            elif today_day == "Friday":
                student = Customer.objects.filter(id=datum["student"]).first()
                if student:
                    student_meal_preference = student.meal_preference
                    if student_meal_preference == "egg" or student_meal_preference == "nonveg":
                        datum["product"] = egg_canteen_product.id
                        datum["rate"] = egg_product_rate
                        datum["total"] = egg_product_rate
                    else:
                        datum["product"] = veg_canteen_product.id
                        datum["rate"] = veg_product_rate
                        datum["total"] = veg_product_rate  
                else:
                    print("Student id came null for friday meal preference")
            else:
                datum["product"] = veg_canteen_product.id
                datum["rate"] = veg_product_rate
                datum["total"] = veg_product_rate                            
        # Serialize and save the attendance records if no existing entries found
        serializer = StudentAttendanceSerializer(data=data, many=True)
        print(data)

        check_studentattendance_forleave(absent_data)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Student canteen attendance created successfully"}, status=200)
            # else:
            #     return Response({"error": f"Data is not valid "}, status=400)
        except Exception as e:
            print(str(e))
            return Response({"error": f"Data is not valid "}, status=400)

class DatewiseStudentAttendanceList(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request, *args, **kwargs):

        data = request.data
        # Ensure the data is always a list
        date = data["date"]
        studentattendance_data = StudentAttendance.objects.filter(eaten_date=date)
        serializer = StudentAttendanceSerializer(studentattendance_data, many=True)

        return Response(serializer.data, 200)
    
from datetime import datetime
from django.db.models import Count, Sum
class DatewiseStudentAggregateAttendanceList(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        data = request.data

        # Extract 'from_date' and 'to_date' from request data
        from_date = data["from_date"]
        to_date = data["to_date"]
        
        student_id = data.get("student_id", None)


        # Ensure date format is correct (optional, depends on your input format)
        from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        if student_id:
            # Query with date range filter
            meal_eatens_by_students = (
                StudentAttendance.objects
                .filter(eaten_date__range=[from_date, to_date], student__id=int(student_id))  # Date range filter
                .values('student', 'student__name', 'student__student_class','student__roll_no', 'student__section', 'rate', 'total' )  
                .annotate(no_of_entries=Count('id'))  
                .order_by('-no_of_entries')  
            )
        # # Query with date range filter
        # meal_eatens_by_students = (
        #     StudentAttendance.objects
        #     .filter(eaten_date__range=[from_date, to_date])  # Date range filter
        #     .values('student', 'student__name', 'student__student_class','student__roll_no', 'student__section', 'rate', 'total' )  
        #     .annotate(no_of_entries=Count('id'))  
        #     .order_by('-no_of_entries')  
        # )
        meal_eatens_by_students = (
            StudentAttendance.objects
            .filter(status=True, is_deleted=False, bill_created=False, eaten_date__range=[from_date, to_date])
            .values('student', 'student__name', 'student__student_class', 'student__roll_no', 'student__section')
            .annotate(no_of_entries=Count('id'), total_sum=Sum('total'))
            .order_by('-no_of_entries')
        )

        studentAttendanceIndividualData = StudentAttendance.objects.filter(eaten_date__range=[from_date, to_date])
        serializer = StudentAttendanceSerializer(studentAttendanceIndividualData, many=True)
        # Convert QuerySet to list for JSON response
        individualDataList = serializer.data
        response_data = list(meal_eatens_by_students)
        # for data in response_data:
        #     no_of_dinein= data["no_of_entries"]
        #     rate = data["rate"]

        #     total = no_of_dinein * rate

        #     data["total"] = total

        for item in individualDataList:
            item["rate"] = float(item["rate"])
            item["total"] = float(item["total"])
        if not response_data:
            return Response({"message": "No attendance records found for the given date range."}, status=200)
        return Response({"aggregated_data" :response_data, "individual_data": individualDataList}, status=200)


from canteen.utils import create_student_bills
class TestCronjob(APIView):
    def get(self, request):
        try:
            create_student_bills()
            return Response("Bill created successfully", 200)
        except Exception as e:
            return Response(str(e), 400)

import nepali_datetime
from product.models import Product
from canteen.utils import convert_amount_to_words
from bill.models import Bill, BillItem
from organization.models import Branch, Organization
import pytz
from bill.utils import product_sold
from django.db import transaction

from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import pytz
from datetime import datetime
import nepali_datetime

class CheckoutCanteenBill(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        data = request.data

        try:
            student_id = int(data.get("student_id", None))
        except (TypeError, ValueError):
            return Response({
                "success": False,
                "message": "Invalid or missing student_id"
            }, status=status.HTTP_400_BAD_REQUEST)

        nepal_tz = pytz.timezone("Asia/Kathmandu")
        transaction_datetime = datetime.now(nepal_tz)
        transaction_date_time = transaction_datetime.strftime("%Y-%m-%d %H:%M:%S")
        transaction_date = transaction_datetime.strftime("%Y-%m-%d")

        student = Customer.objects.filter(id=student_id).first()
        if not student:
            return Response({
                "success": False,
                "message": f"Student with ID {student_id} not found!"
            }, status=status.HTTP_404_NOT_FOUND)

        attendances = (
            StudentAttendance.objects
            .filter(student=student, bill_created=False)
            .values('product', 'rate')
            .annotate(no_of_entries=Count('id'))
        )

        if not attendances:
            return Response({
                "success": False,
                "message": f"No pending attendance records found for {student.name}."
            }, status=status.HTTP_400_BAD_REQUEST)

        branch = Branch.objects.active().filter(is_central_billing=True).last()
        if not branch:
            return Response({
                "success": False,
                "message": "No active central billing branch found!"
            }, status=status.HTTP_400_BAD_REQUEST)

        bill_items = []
        sub_total = 0

        for att in attendances:
            product = Product.objects.filter(id=att['product']).first()
            if not product:
                continue
            quantity = att['no_of_entries']
            rate = float(att['rate'])
            amount = quantity * rate
            sub_total += amount

            bill_item = BillItem.objects.create(
                product_quantity=quantity,
                rate=rate,
                product_title=product.title,
                unit_title=product.unit,
                amount=amount,
                product=product
            )
            product_sold(bill_item)
            bill_items.append(bill_item)

        tax_amount = sub_total * 0.13
        taxable_amount = sub_total
        grand_total = sub_total + tax_amount
        amount_in_words = convert_amount_to_words(grand_total)

        nepali_today = nepali_datetime.date.today()

        bill = Bill.objects.create(
            branch=branch,
            transaction_miti=nepali_today,
            agent=None,
            agent_name='',
            terminal=1,
            customer_name=student.name,
            customer_address=student.address,
            customer_tax_number='',
            customer=student,
            transaction_date_time=transaction_date_time,
            transaction_date=transaction_date,
            sub_total=sub_total,
            discount_amount=0.0,
            taxable_amount=taxable_amount,
            tax_amount=tax_amount,
            grand_total=grand_total,
            service_charge=0.0,
            amount_in_words=amount_in_words,
            organization=Organization.objects.last(),
            print_count=1,
            payment_mode='Credit'
        )

        bill.bill_items.add(*bill_items)

        # Mark those attendance records as billed
        StudentAttendance.objects.filter(student=student, bill_created=False).update(bill_created=True)

        return Response({
            "bill_id": bill.id,
            "success": True,
            "message": f"Bill created successfully for {student.name}"
        }, status=status.HTTP_200_OK)
        
from canteen.utils import create_student_bills_for_class, create_advance_bills_for_class
class CheckoutClassBills(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        data = request.data

        student_class = data.get("class", None)

        if student_class:
            try:
                # create_student_bills_for_class(student_class)
                create_advance_bills_for_class(student_class)
                return Response({"data": f"Bills created for class {student_class}"}, 200)
            except Exception as e:
                print(f"Error in creating bill for class {student_class} with {e}")
                return Response({"error": f"Error in creating bills for class {student_class}", }, 400)
        else:
            print("Student class cannot be none")
            return Response({"error": "No class provided"}, 400)

from rest_framework.response import Response
from rest_framework import status
import jwt
from user.models import User
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class VerifyToken(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        
        # Get token from query parameter instead of headers
        token = request.GET.get('token')

        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=int(payload['user_id']))

            # Return user details
            return Response({'valid': True})

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

from user.models import Customer
from canteen.models import PreInformedLeave

class StudentsServedData(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        from datetime import datetime
        from django.utils import timezone

        now = timezone.now()  # safer for timezone-aware datetimes

        try:
            total_no_students = Customer.objects.filter(student_class__isnull=False, status=True, is_deleted=False).count()

            total_students_served_today = StudentAttendance.objects.filter(eaten_date=now.date(),status=True,
                    is_deleted=False).count()
            
            total_no_students_on_leave = PreInformedLeave.objects.filter(start_date__lte=now.date(),end_date__gte=now.date()).count()
                
            today_data = {
                    "total_no_students": total_no_students,
                    "total_students_served": total_students_served_today,
                    "total_no_of_students_to_serve": total_no_students -  total_no_students_on_leave 
                }



            total_students_served_month = StudentAttendance.objects.filter(
                    eaten_date__year=now.year,
                    eaten_date__month=now.month,
                    status=True,
                    is_deleted=False
                ).count()
            month_data = {
                    "total_no_students": total_no_students,
                    "total_students_served": total_students_served_month
                }
            data = {
                "today": today_data,
                "month": month_data
            }
            return Response(data, 200)
        except Exception as e :
            return Response({"error": str(e)}, 400)