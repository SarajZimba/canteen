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