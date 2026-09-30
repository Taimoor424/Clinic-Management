from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from base import models as base_models
from doctor import models as doctor_models
from patient import models as patient_models
from base.utils import send_custom_email
from doctor.models import Doctor
from .forms import AppointmentForm,ContactForm
from django.core.mail import send_mail
from django.conf import settings
from base.models import Blog,BlogCategory,Appointment
from django.db.models import Q
from django.core.paginator import Paginator
from base.models import Appointment, Prescription, Medicine
import cohere
from base.models import Appointment
import json

def symptom_checker(request):
    response_text = ""
    
    if request.method == "POST":
        symptom_input = request.POST.get("symptom", "").strip()
        
        if symptom_input:  # Only continue if input is not empty
            co = cohere.Client(settings.COHERE_API_KEY)

            response = co.generate(
                model='command-r-plus',  
                prompt=f"User has the following symptoms: {symptom_input}. Suggest possible homeopathic medicines and health tips in English and Urdu.",
                max_tokens=300
            )

            response_text = response.generations[0].text
        else:
            response_text = "⚠️ Please enter some symptoms to get a recommendation."

    return render(request, "base/symptom_checker.html", {"response_text": response_text})




def prescription_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id, doctor__user=request.user)
    prescriptions = Prescription.objects.filter(appointment=appointment)

    return render(request, "doctor/prescription_template.html"), {
        "appointment": appointment,
        "prescription": Prescription,
    }

@login_required
def add_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)

    if request.method == "POST":
        medications = request.POST.getlist("medication[]")
        dosages = request.POST.getlist("dosage[]")
        frequencies = request.POST.getlist("frequencie[]")
        durations = request.POST.getlist("duration[]")
        instructions = request.POST.get("instructions")

        all_rows = []
        for med, dose, freq, dur in zip(medications, dosages, frequencies, durations):
            all_rows.append({
                "medication": med,
                "dosage": dose,
                "frequency": freq,
                "duration": dur
            })

        # Save all medication data as a JSON string in the medications field
        Prescription.objects.create(
            appointment=appointment,
            medications=json.dumps(all_rows),
            instructions=instructions
        )

        messages.success(request, "Prescription added successfully.")
        return redirect("doctor:appointment_detail", appointment_id=appointment_id)

    return redirect("doctor:appointment_detail", appointment_id=appointment_id)



def blog_detail(request, blog_id):
    blog = Blog.objects.get(id=blog_id)

    # Example: fetch related blogs by category (excluding current)
    related_blogs = Blog.objects.filter(
        Q(category=blog.category) & ~Q(id=blog.id)
    ).order_by('-created_at')[:4]

    return render(request, 'base/blog_detail.html', {
        'blog': blog,
        'related_blogs': related_blogs
    })

def contact_view(request):
    form = ContactForm()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            instance = form.save()

            # Send email
            subject = form.cleaned_data['subject']
            message = f"Message from {form.cleaned_data['name']} <{form.cleaned_data['email']}>\n\n{form.cleaned_data['message']}"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = ['taimoor974@example.com']  # 👈 Your target email

            send_mail(subject, message, from_email, to_email)
            messages.success(request, "Your message has been submitted successfully.")


            return redirect('base:contact_view')  # redirect after submission

    return render(request, 'base/contact.html', {'form': form})




import cohere  # Make sure `cohere` is installed: pip install cohere

def index(request):
    doctors = Doctor.objects.all()
    services = base_models.Service.objects.all()
    response_text = None

    if request.method == "POST":
        symptom = request.POST.get("symptom", "").strip()
        if symptom:  # Only proceed if symptom is not empty
            co = cohere.Client(settings.COHERE_API_KEY)
            prompt = f"User symptoms: {symptom}\nGive some health advice, possible disease, and homeopathic medicine suggestions in both English and Urdu."

            try:
                response = co.generate(prompt=prompt, max_tokens=300)
                response_text = response.generations[0].text.strip()
            except Exception as e:
                response_text = f"❌ Failed to get response: {str(e)}"
        else:
            response_text = "⚠️ Please enter symptoms before submitting."

    context = {
        'services': services,
        'doctors': doctors,
        'response_text': response_text,
    }

    return render(request, "base/index.html", context)
def service_detail(request, service_id):
    service = base_models.Service.objects.get(id=service_id)
    return render(request, "base/service_detail.html", {'service': service})
def book_appointment(request, service_id, doctor_id):
    service = get_object_or_404(base_models.Service, id=service_id)
    doctor = get_object_or_404(doctor_models.Doctor, id=doctor_id)
    patient = get_object_or_404(patient_models.Patient, user=request.user)

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # ✅ Update patient info
            patient.full_name = cd["full_name"]
            patient.email = cd["email"]
            patient.mobile = cd["mobile"]
            patient.gender = cd["gender"]
            patient.save()

            # ✅ Create appointment
            appointment = base_models.Appointment.objects.create(
                service=service,
                doctor=doctor,
                patient=patient,
                appointment_date=doctor.next_available_appointment_date,
                issues=cd["issues"],
                status="Scheduled"
            )

            # ✅ Send email to patient
            subject_patient = "Appointment Confirmation"
            message_patient = f"""
Dear {patient.full_name},

Your appointment with  {doctor.full_name} for {service.name} is confirmed.

 Date: {appointment.appointment_date}
 Doctor:  {doctor.full_name}
 Service: {service.name}

Thank you for choosing our clinic!
"""
            send_custom_email(subject_patient, message_patient, [patient.email])

            # ✅ Send email to doctor
            subject_doctor = "New Appointment Scheduled"
            message_doctor = f"""
Dear  {doctor.full_name},

A new appointment has been booked.

 Patient: {patient.full_name}
 Mobile: {patient.mobile}
 Email: {patient.email}
 Date: {appointment.appointment_date}
 Service: {service.name}
 Issues: {appointment.issues}

Please check your schedule.

Regards,
Clinic Management System
"""
            send_custom_email(subject_doctor, message_doctor, [doctor.email])

            # ✅ Create Notification for Doctor
            doctor_models.Notification.objects.create(
                doctor=doctor,
                appointment=appointment,
                type=f"New Appointment from {patient.full_name}",
                

                seen=False
            )

            messages.success(request, "Appointment booked successfully!")
            form = AppointmentForm()  # Clear the form
            return render(request, "base/book_appointment.html", {
            "service": service,
            "doctor": doctor,
            "patient": patient,
            "form": form,
        })
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentForm(initial={
            "full_name": patient.full_name,
            "email": patient.email,
            "mobile": patient.mobile,
            "gender": patient.gender,
        })

    return render(request, "base/book_appointment.html", {
        "service": service,
        "doctor": doctor,
        "patient": patient,
        "form": form,
    })

def about(request):
    doctors = Doctor.objects.all()
    return render(request, "base/about.html", {"doctors": doctors})

def blogs(request):
    selected_category = request.GET.get('category')

    if selected_category:
        blogs = Blog.objects.filter(category__slug=selected_category).order_by('-created_at')
    else:
        blogs = Blog.objects.all().order_by('-created_at')

    paginator = Paginator(blogs, 10)  # Show 10 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'blogs': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'featured_blog': Blog.objects.first(),  # Optional: highlight latest or specific blog
        'categories': BlogCategory.objects.all(),
        'selected_category': selected_category,
    }
    return render(request, 'base/blogs.html', context)

def services(request):
 services = base_models.Service.objects.all()
 context = {
        'services': services
    }
 return render(request, "base/services.html", context)
def doctors_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'partials/team.html', {'doctors': doctors})


def medicine_store(request):
    medicines = Medicine.objects.filter(stock__gt=0)  # show only in-stock medicines
    return render(request, 'store/medicine_list.html', {'medicines': medicines})


