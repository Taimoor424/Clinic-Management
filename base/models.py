from django.db import models
from shortuuid.django_fields import ShortUUIDField
from doctor import models as doctor_models
from patient import models as patient_models
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field 
from django.utils import timezone

class Service(models.Model):
    image = models.FileField(upload_to="images", null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    available_doctors = models.ManyToManyField(doctor_models.Doctor, blank=True)

    def __str__(self):
        return f"{self.name} - {self.cost}"
    


class Appointment(models.Model):
    STATUS = [
        ('Scheduled', 'Scheduled'), 
        ('Completed', 'Completed'), 
        ('Pending', 'Pending'), 
        ('Cancelled', 'Cancelled')
    ]
    
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_appointments')
    doctor = models.ForeignKey(doctor_models.Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctor_appointments')
    patient = models.ForeignKey(patient_models.Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_patient')
    appointment_date = models.DateTimeField(null=True, blank=True)
    issues = models.TextField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    appointment_id = ShortUUIDField(length=6, max_length=10, alphabet="1234567890")
    status = models.CharField(max_length=120, choices=STATUS)
    created_at = models.DateTimeField(default=timezone.now, null=False, blank=False)



    def __str__(self):
       patient_name = self.patient.full_name if self.patient else "Unknown Patient"
       doctor_name = self.doctor.full_name if self.doctor else "Unknown Doctor"
       return f"{patient_name} with {doctor_name}"
   



class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    medications = models.TextField(blank=True, null=True)
    
    dosage = models.CharField(max_length=100, blank=True, null=True)
    frequency = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)

    instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Prescription for {self.appointment.patient.full_name}"
class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Blog Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='blog_images/', default='default.jpg')
    content = CKEditor5Field('Content', config_name='default')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name="blogs")
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    class Meta:
        verbose_name = "User Query"
        verbose_name_plural = "User Queries"

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='medicines/')
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


