from bill.models import Bill
from django.db.models import Count
from canteen.models import StudentAttendance
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from bill.models import Bill, BillItem
from organization.models import Organization, Branch
from product.models import Product, BranchStock
from user.models import Customer
import nepali_datetime
from bill.utils import product_sold
import pytz
from datetime import datetime
from django.db import transaction


@transaction.atomic  # Decorator to wrap the entire function in a single transaction
def create_student_bills():

    # Define Nepal Timezone
    nepal_tz = pytz.timezone("Asia/Kathmandu")

    # Get current date and time in Nepal Time Zone
    transaction_datetime = datetime.now(nepal_tz)
    transaction_date_time = transaction_datetime.strftime("%Y-%m-%d %H:%M:%S")  # Format: 2025-04-01 14:30:45
    transaction_date = transaction_datetime.strftime("%Y-%m-%d")  # Format: 2025-04-01
    meal_eatens_by_students = (
        StudentAttendance.objects
        .filter(bill_created=False)
        .values('student')  # Returns a list of dicts
        .annotate(no_of_entries=Count('id'))  # Count entries per student
        .order_by('-no_of_entries')  # Optional: Sort by most meals eaten
    )

    print(meal_eatens_by_students)

    item = Product.objects.filter(is_canteen_item=True).first()
    if not item:
        print("No canteen item found!")
        return

    branch = Branch.objects.active().filter(is_central_billing=True).last()
    if not branch:
        print("No active central billing branch found!")
        return
    student_attendance_updates = []
    for entry in meal_eatens_by_students:
        student_id = entry['student']  # Get student ID
        quantity = entry['no_of_entries']  # Get count of meals eaten

        student = Customer.objects.filter(id=student_id).first()
        if not student:
            print(f"Student with ID {student_id} not found!")
            continue  # Skip this iteration if student is not found

        nepali_today = nepali_datetime.date.today()


        # Bill details
        transaction_miti = nepali_today
        terminal = 1
        customer_name = student.name
        customer_address = student.address
        customer_tax_number = ''

        sub_total = quantity * item.price
        taxable_amount = quantity * item.price
        grand_total = sub_total
        amount_in_words = convert_amount_to_words(grand_total)

        # Create Bill
        bill = Bill.objects.create(
            branch=branch,
            transaction_miti=transaction_miti,
            agent=None,
            agent_name='',
            terminal=terminal,
            customer_name=customer_name,
            customer_address=customer_address,
            customer_tax_number=customer_tax_number,
            customer=student,
            transaction_date_time=transaction_date_time,
            transaction_date=transaction_date,
            sub_total=sub_total,
            discount_amount=0.0,
            taxable_amount=taxable_amount,
            tax_amount=0.0,
            grand_total=grand_total,
            service_charge=0.0,
            amount_in_words=amount_in_words,
            organization=Organization.objects.last(),
            print_count=1,
            payment_mode='Credit'
        )

        bill_items = []

        try:
            bill_item = BillItem.objects.create(
                product_quantity=quantity,
                rate=item.price,
                product_title=item.title,
                unit_title=item.unit,
                amount=quantity * item.price,
                product=item
            )

            product_sold(bill_item)  # Call your product_sold function

            bill_items.append(bill_item)
            bill.bill_items.add(*bill_items)
        except Exception as e:
            print("Exception:", e)
            continue
        student_attendance_updates.append(student)
        # ✅ **Update `bill_created` status for all associated StudentAttendance records**
        # StudentAttendance.objects.filter(student=student, bill_created=False).update(bill_created=True)

        print(f"Bill created successfully for {student.name}!")

    # Bulk update the `bill_created` status for all associated StudentAttendance records
    StudentAttendance.objects.filter(student__in=student_attendance_updates, bill_created=False).update(bill_created=True)

import inflect

def convert_amount_to_words(amount):
    p = inflect.engine()

    # Split the amount into integer and decimal parts
    rupees = int(amount)
    paisa = round((amount - rupees) * 100)

    # Convert the rupees and paisa to words
    rupees_in_words = p.number_to_words(rupees).replace(",", "")
    paisa_in_words = p.number_to_words(paisa).replace(",", "")

    # Format the final string
    if paisa > 0:
        amount_in_words = f"{rupees_in_words} rupees and {paisa_in_words} paisa"
    else:
        amount_in_words = f"{rupees_in_words} rupees"
    return amount_in_words


from collections import defaultdict

@transaction.atomic
def create_student_bills_for_class(student_class):
    nepal_tz = pytz.timezone("Asia/Kathmandu")
    transaction_datetime = datetime.now(nepal_tz)
    transaction_date_time = transaction_datetime.strftime("%Y-%m-%d %H:%M:%S")
    transaction_date = transaction_datetime.strftime("%Y-%m-%d")

    # Get grouped meal entries
    meal_entries = (
        StudentAttendance.objects
        .filter(bill_created=False, student__student_class=student_class)
        .values('student', 'product', 'rate')
        .annotate(no_of_entries=Count('id'))
    )

    # Group entries by student
    student_meals = defaultdict(list)
    for entry in meal_entries:
        student_meals[entry['student']].append(entry)

    branch = Branch.objects.active().filter(is_central_billing=True).last()
    if not branch:
        print("No active central billing branch found!")
        return

    students_to_update = []

    for student_id, items in student_meals.items():
        student = Customer.objects.filter(id=student_id).first()
        if not student:
            continue

        nepali_today = nepali_datetime.date.today()
        transaction_miti = nepali_today
        terminal = 1

        sub_total = 0
        bill_items = []

        for item_data in items:
            product = Product.objects.filter(id=item_data['product']).first()
            if not product:
                continue

            quantity = item_data['no_of_entries']
            rate = float(item_data['rate'])
            item_total = quantity * rate
            sub_total += item_total

            bill_item = BillItem.objects.create(
                product_quantity=quantity,
                rate=rate,
                product_title=product.title,
                unit_title=product.unit,
                amount=item_total,
                product=product
            )

            product_sold(bill_item)
            bill_items.append(bill_item)


        tax_amount = sub_total * 0.13
        taxable_amount = sub_total
        grand_total = sub_total + tax_amount
        amount_in_words = convert_amount_to_words(grand_total)

        bill = Bill.objects.create(
            branch=branch,
            transaction_miti=transaction_miti,
            agent=None,
            agent_name='',
            terminal=terminal,
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
        students_to_update.append(student)

        print(f"Bill created for {student.name} with {len(bill_items)} item(s)")

    # Mark attendance as billed
    StudentAttendance.objects.filter(student__in=students_to_update, bill_created=False).update(bill_created=True)




from datetime import timedelta
from canteen.models import PreInformedLeave, tblmissedattendance
def check_studentattendance_forleave(data):
    
    # If no attendance data provided, nothing to check
    if not data:
        return
        
    # Get the date from the first attendance record (all should be same date)
    attendance_date_str = data[0].get("date")
    try:
        attendance_date = datetime.strptime(attendance_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        print("Invalid date format in attendance data")
        return
    
    # Get day of week from the date
    day_of_week = attendance_date.strftime("%A")
    
    # # Get list of student IDs who are present (have attendance)
    # present_student_ids = [entry.get("student") for entry in data if entry.get("student")]
    
    absent_student_ids = [entry.get("student") for entry in data if entry.get("student")]

    # # Find students who are absent (not in present list)
    # absent_students = all_students.filter(id__in=absent_student_ids)

    veg_canteen_product = Product.objects.filter(is_canteen_item=True, lunch_type="veg").first()
    veg_product_rate = veg_canteen_product.price if veg_canteen_product else 0.0

    if not veg_canteen_product:
        print("Warning: Veg product type is missing")
        return

    nonveg_canteen_product = Product.objects.filter(is_canteen_item=True, lunch_type="nonveg").first()
    nonveg_product_rate = nonveg_canteen_product.price if nonveg_canteen_product else 0.0
    if not nonveg_canteen_product:
        print("Warning: Non veg product type is missing")
        return
    egg_canteen_product = Product.objects.filter(is_canteen_item=True, lunch_type="egg").first()
    egg_product_rate = egg_canteen_product.price if egg_canteen_product else 0.0

    if not egg_canteen_product:
        print("Warning: Egg product type is missing")
        return
    
    for student_id in absent_student_ids:
        student = Customer.objects.filter(id=student_id).first()

        if not student:
            print(f"Invalid id for student {student_id}")
            continue  # Skip just this student
        # Check if student has pre-informed leave for this date

        if check_if_absentdata_already_populated(student, attendance_date):
            continue
        has_preinformed_leave = PreInformedLeave.objects.filter(
            student=student,
            start_date__lte=attendance_date,
            end_date__gte=attendance_date
        ).exists()
        
        if has_preinformed_leave:

            if day_of_week == "Wednesday":   

                student_meal_preference = student.meal_preference

                if student_meal_preference == "nonveg":
                    missed_product = nonveg_canteen_product
                else:
                    missed_product = veg_canteen_product

            elif day_of_week == "Friday":
                student_meal_preference = student.meal_preference
                if student_meal_preference == "egg" or student_meal_preference == "nonveg":
                    missed_product = egg_canteen_product
                else:
                    missed_product = veg_canteen_product
            else:
                missed_product = veg_canteen_product


            tblmissedattendance.objects.create(
                student=student,
                Lunchtype=student.meal_preference,
                missed_date=attendance_date,
                day=day_of_week,
                pre_informed=True,
                product=missed_product
            )
            print(f"student {student.name} missed {missed_product.title} on {day_of_week} and {attendance_date} with preinform True")
        else:
            # Check attendance for previous 2 days
            prev_day1 = attendance_date - timedelta(days=1)
            prev_day2 = attendance_date - timedelta(days=2)
            
            # Check if student was absent both previous days
            was_absent_prev_day1 = not StudentAttendance.objects.filter(
                student=student,
                eaten_date=prev_day1 
            ).exists()
            
            was_absent_prev_day2 = not StudentAttendance.objects.filter(
                student=student,
                eaten_date=prev_day2
            ).exists()
            
            if was_absent_prev_day1 and was_absent_prev_day2:
                # Create missed attendance record with pre_informed=False

                if day_of_week == "Wednesday":   

                    student_meal_preference = student.meal_preference

                    if student_meal_preference == "nonveg":
                        missed_product = nonveg_canteen_product
                    else:
                        missed_product = veg_canteen_product

                elif day_of_week == "Friday":
                    student_meal_preference = student.meal_preference
                    if student_meal_preference == "egg" or student_meal_preference == "nonveg":
                        missed_product = egg_canteen_product
                    else:
                        missed_product = veg_canteen_product
                else:
                    missed_product = veg_canteen_product
                tblmissedattendance.objects.create(
                    student=student,
                    Lunchtype=student.meal_preference,
                    missed_date=attendance_date,
                    day=day_of_week,
                    pre_informed=False,
                    product=missed_product
                )

                print(f"student {student.name} missed {missed_product.title} on {day_of_week} and {attendance_date} with preinform False")

def check_if_absentdata_already_populated(student, attendance_date):
    if tblmissedattendance.objects.filter(student=student, missed_date= attendance_date).exists():
        return True
    else:
        return False
from collections import defaultdict
from canteen.models import WorkingDays
from nepali_datetime import date as nepali_date
from django.db import transaction
from datetime import datetime
import pytz

@transaction.atomic
def create_advance_bills_for_class(student_class):
    nepal_tz = pytz.timezone("Asia/Kathmandu")
    now = datetime.now(nepal_tz)
    transaction_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    transaction_date = now.strftime("%Y-%m-%d")
    transaction_miti = nepali_date.today()

    # Get current month's first and last day dynamically
    current_month_start = now.replace(day=1)
    next_month = current_month_start.replace(month=current_month_start.month+1) if current_month_start.month < 12 else current_month_start.replace(year=current_month_start.year+1, month=1)
    current_month_end = next_month - timedelta(days=1)
    
    working_days = WorkingDays.objects.filter(
        working_date__gte=current_month_start.date(),
        working_date__lte=current_month_end.date()
    ).values_list('working_date', flat=True).order_by('working_date')

    if not working_days.exists():
        message = "No working days found for current_month"
        print(f"No working days found for {current_month_start.strftime('%B %Y')}")
        return message

    # Prepare product references
    veg_product = Product.objects.filter(is_canteen_item=True, lunch_type="veg").first()
    egg_product = Product.objects.filter(is_canteen_item=True, lunch_type="egg").first()
    nonveg_product = Product.objects.filter(is_canteen_item=True, lunch_type="nonveg").first()

    if not veg_product:
        print("Veg product missing. Cannot proceed.")
        return

    branch = Branch.objects.active().filter(is_central_billing=True).last()
    if not branch:
        print("No central billing branch found")
        return

    students = Customer.objects.filter(student_class=student_class)

    for student in students:
        # Initialize counters
        product_counter = defaultdict(int)
        
        # # Get all missed attendance records for current month that haven't been considered yet
        # missed_meals = tblmissedattendance.objects.filter(
        #     student=student,
        #     considered_next_month=False,
        #     missed_date__gte=current_month_start.date(),
        #     missed_date__lte=current_month_end.date()
        # )

        # Get first and last day of previous month
        if current_month_start.month == 1:
            prev_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
        else:
            prev_month_start = current_month_start.replace(month=current_month_start.month - 1)

        prev_month_end = current_month_start - timedelta(days=1)

        # Now use this for filtering missed_meals
        missed_meals = tblmissedattendance.objects.filter(
            student=student,
            considered_next_month=False,
            missed_date__gte=prev_month_start.date(),
            missed_date__lte=prev_month_end.date()
        )
        
        # Count all working days in current month
        for day in working_days:
            day_name = day.strftime("%A")
            preference = student.meal_preference

            if day_name == "Wednesday":
                if preference == "nonveg" and nonveg_product:
                    product_counter[nonveg_product.id] += 1
                else:
                    product_counter[veg_product.id] += 1
            elif day_name == "Friday":
                if preference in ["egg", "nonveg"] and egg_product:
                    product_counter[egg_product.id] += 1
                else:
                    product_counter[veg_product.id] += 1
            else:
                product_counter[veg_product.id] += 1
        
        # Subtract the missed meals
        for missed_meal in missed_meals:
            if missed_meal.product:
                product_id = missed_meal.product.id
                if product_id in product_counter:
                    product_counter[product_id] -= 1
                    if product_counter[product_id] < 0:
                        product_counter[product_id] = 0
                missed_meal.considered_next_month = True
                missed_meal.save()

        # Remove products with zero quantity
        product_counter = {k: v for k, v in product_counter.items() if v > 0}

        bill_items = []
        sub_total = 0

        for product_id, quantity in product_counter.items():
            product = Product.objects.filter(id=product_id).first()
            if not product:
                continue
            rate = float(product.price)
            amount = rate * quantity
            sub_total += amount

            bill_item = BillItem.objects.create(
                product_quantity=quantity,
                rate=rate,
                product_title=product.title,
                unit_title=product.unit,
                amount=amount,
                product=product
            )
            bill_items.append(bill_item)

        tax_amount = sub_total * 0.13
        grand_total = sub_total + tax_amount
        amount_in_words = convert_amount_to_words(grand_total)

        bill = Bill.objects.create(
            branch=branch,
            transaction_miti=transaction_miti,
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
            taxable_amount=sub_total,
            tax_amount=tax_amount,
            grand_total=grand_total,
            service_charge=0.0,
            amount_in_words=amount_in_words,
            organization=Organization.objects.last(),
            print_count=1,
            payment_mode='Credit'
        )

        bill.bill_items.add(*bill_items)
        print(f"Advance bill created for {student.name}: {len(bill_items)} items (Month: {current_month_start.strftime('%B %Y')})")