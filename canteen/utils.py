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


# @transaction.atomic  # Decorator to wrap the entire function in a single transaction
# def create_student_bills_for_class(student_class):

#     # Define Nepal Timezone
#     nepal_tz = pytz.timezone("Asia/Kathmandu")

#     # Get current date and time in Nepal Time Zone
#     transaction_datetime = datetime.now(nepal_tz)
#     transaction_date_time = transaction_datetime.strftime("%Y-%m-%d %H:%M:%S")  # Format: 2025-04-01 14:30:45
#     transaction_date = transaction_datetime.strftime("%Y-%m-%d")  # Format: 2025-04-01
#     meal_eatens_by_students = (
#         StudentAttendance.objects
#         .filter(bill_created=False,student__student_class=student_class)
#         .values('student', 'product', 'rate')
#         .annotate(no_of_entries=Count('id'))  # Count entries per student
#         .order_by('-no_of_entries')  # Optional: Sort by most meals eaten
#     )

#     print(f"meal eaten",meal_eatens_by_students)

#     item = Product.objects.filter(is_canteen_item=True).first()
#     if not item:
#         print("No canteen item found!")
#         return

#     branch = Branch.objects.active().filter(is_central_billing=True).last()
#     if not branch:
#         print("No active central billing branch found!")
#         return
#     student_attendance_updates = []
#     for entry in meal_eatens_by_students:
#         student_id = entry['student']  # Get student ID
#         quantity = entry['no_of_entries']  # Get count of meals eaten

#         student = Customer.objects.filter(id=student_id).first()
#         if not student:
#             print(f"Student with ID {student_id} not found!")
#             continue  # Skip this iteration if student is not found

#         nepali_today = nepali_datetime.date.today()


#         # Bill details
#         transaction_miti = nepali_today
#         terminal = 1
#         customer_name = student.name
#         customer_address = student.address
#         customer_tax_number = ''

#         sub_total = quantity * item.price
#         taxable_amount = quantity * item.price
#         tax_amount = taxable_amount * 0.13
#         grand_total = sub_total + tax_amount
#         amount_in_words = convert_amount_to_words(grand_total)



#         # Create Bill
#         bill = Bill.objects.create(
#             branch=branch,
#             transaction_miti=transaction_miti,
#             agent=None,
#             agent_name='',
#             terminal=terminal,
#             customer_name=customer_name,
#             customer_address=customer_address,
#             customer_tax_number=customer_tax_number,
#             customer=student,
#             transaction_date_time=transaction_date_time,
#             transaction_date=transaction_date,
#             sub_total=sub_total,
#             discount_amount=0.0,
#             taxable_amount=taxable_amount,
#             tax_amount=tax_amount,
#             grand_total=grand_total,
#             service_charge=0.0,
#             amount_in_words=amount_in_words,
#             organization=Organization.objects.last(),
#             print_count=3,
#             payment_mode='Credit'
#         )

#         bill_items = []

#         try:
#             bill_item = BillItem.objects.create(
#                 product_quantity=quantity,
#                 rate=item.price,
#                 product_title=item.title,
#                 unit_title=item.unit,
#                 amount=quantity * item.price,
#                 product=item
#             )

#             product_sold(bill_item)  # Call your product_sold function

#             bill_items.append(bill_item)
#             bill.bill_items.add(*bill_items)
#         except Exception as e:
#             print("Exception:", e)
#             continue
#         student_attendance_updates.append(student)
#         # ✅ **Update `bill_created` status for all associated StudentAttendance records**
#         # StudentAttendance.objects.filter(student=student, bill_created=False).update(bill_created=True)

#         print(f"Bill created successfully for {student.name}!")

#     # Bulk update the `bill_created` status for all associated StudentAttendance records
#     StudentAttendance.objects.filter(student__in=student_attendance_updates, bill_created=False).update(bill_created=True)


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


        tax_amount = (sub_total * 13)/113
        taxable_amount = sub_total - tax_amount
        # grand_total = sub_total #because price is tax inclusive that is tax is already included in the price of product
        sub_total = taxable_amount #for getting price before tax
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
