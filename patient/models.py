from django.db import models
from django.utils import timezone

from userauths import models as userauths_models

NOTIFICATION_TYPE = (
    ("Appointment Scheduled", "Appointment Scheduled"),
    ("Appointment Cancelled", "Appointment Cancelled"),
)

class Patient(models.Model):
    user = models.OneToOneField(userauths_models.User, on_delete=models.CASCADE)
    image = models.FileField(upload_to="images", null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField(default=timezone.now, null=True, blank=True)
    blood_group = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    @property
    def created_date(self):
        return self.created_at.strftime('%Y-%m-%d') if self.created_at else "N/A"

    def __str__(self):
        return f"{self.full_name}"
    
NOTIFICATION_TYPE = [
    ('Appointment Booked', 'Appointment Booked'),
    ('Appointment Cancelled', 'Appointment Cancelled'),
    ('Prescription Added', 'Prescription Added'),
    ('Order Placed', 'Order Placed'),
]

class Notification(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    appointment = models.ForeignKey("base.Appointment", on_delete=models.CASCADE, null=True, blank=True, related_name="patient_appointment_notification")
    type = models.CharField(max_length=100, choices=NOTIFICATION_TYPE)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} Notification"