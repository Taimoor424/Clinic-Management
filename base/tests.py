from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from base.models import Appointment, Prescription, Service
from doctor.models import Doctor
from patient.models import Patient
from base.views import prescription_detail


class PrescriptionDetailViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()

        self.doctor_user = User.objects.create_user(
            email='doctor@example.com',
            username='doctor',
            password='StrongPass123!',
            user_type='Doctor',
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            full_name='Dr. Smith',
            email=self.doctor_user.email,
        )

        self.patient_user = User.objects.create_user(
            email='patient@example.com',
            username='patient',
            password='StrongPass123!',
            user_type='Patient',
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            full_name='John Doe',
            email=self.patient_user.email,
        )

        self.service = Service.objects.create(
            name='General Consultation',
            description='Regular health check-up',
            cost='150.00',
        )

        self.appointment = Appointment.objects.create(
            service=self.service,
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=timezone.now(),
            issues='Headache and fever',
            status='Scheduled',
        )

        self.prescription = Prescription.objects.create(
            appointment=self.appointment,
            medications='[{"medication": "Paracetamol", "dosage": "500mg"}]',
            instructions='Take after food',
        )

    def test_prescription_detail_returns_http_response_with_prescriptions(self):
        request = self.factory.get('/')
        request.user = self.doctor_user

        response = prescription_detail(request, self.appointment.appointment_id)

        self.assertEqual(response.status_code, 200)
        self.assertIn('prescriptions', response.context_data)
        self.assertIn(self.prescription, response.context_data['prescriptions'])
