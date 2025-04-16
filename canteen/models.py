from django.db import models

from root.utils import BaseModel
from user.models import Customer

from product.models import Product

# Create your models here.

class StudentAttendance(BaseModel):
    student = models.ForeignKey(Customer, models.CASCADE, null=True, blank=True)
    eaten_date = models.DateField(null=True, blank=True)
    bill_created = models.BooleanField(default=False)
    rate =  models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total =  models.DecimalField(max_digits=10, decimal_places=2, default=0)
    product = models.ForeignKey(Product, models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.student.name} ({self.eaten_date})"
    
class WorkingDays(BaseModel):
    working_date = models.DateField(null=True, blank=True)

class PreInformedLeave(BaseModel):
    student = models.ForeignKey(Customer, models.CASCADE, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)


class tblmissedattendance(BaseModel):
    student = models.ForeignKey(Customer, models.CASCADE, null=True, blank=True)
    Lunchtype = models.CharField(max_length=255, null=True, blank=True)
    missed_date = models.DateField(null=True, blank=True)
    day = models.CharField(max_length=255, null=True, blank=True)
    pre_informed = models.BooleanField(null=True, blank=True)
