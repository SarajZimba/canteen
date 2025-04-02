from django.db import models

from root.utils import BaseModel
from user.models import Customer

# Create your models here.

class StudentAttendance(BaseModel):
    student = models.ForeignKey(Customer, models.CASCADE, null=True, blank=True)
    eaten_date = models.DateField(null=True, blank=True)
    bill_created = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} ({self.eaten_date})"