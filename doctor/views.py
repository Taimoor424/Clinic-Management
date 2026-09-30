from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from doctor import models as doctor_models
from base import models as base_models
from django.http import Http404
from base.models import Prescription
from base.models import Appointment
from doctor.models import Notification
from django.db.models import Q
from django.core.paginator import Paginator
from patient.models import Notification as PatientNotification





@login_required
def dashboard(request):
    doctor = request.user.doctor

    appointments = Appointment.objects.filter(
        doctor=doctor
    ).exclude(status__iexact="Completed").order_by('-appointment_date')

    prescriptions = Prescription.objects.filter(
        appointment__doctor=doctor
    ).order_by('-created_at')[:10]

    # ✅ Include unseen notifications via appointment link
    
    unseen_notifications = Notification.objects.filter(
        doctor=doctor,
        seen=False
    )

    context = {
        'appointments': appointments,
        'prescriptions': prescriptions,
        'unseen_notifications': unseen_notifications,
        'unseen_count': unseen_notifications.count(),
    }

    return render(request, 'doctor/dashboard.html', context)
@login_required
def appointments(request):
    doctor = doctor_models.Doctor.objects.get(user=request.user)
    search_query = request.GET.get("search", "")

    appointments = base_models.Appointment.objects.filter(doctor=doctor)

    if search_query:
        appointments = appointments.filter(
            Q(patient__full_name__icontains=search_query)
        )

    context = {
        "appointments": appointments,
        "search_query": search_query,
    }

    return render(request, "doctor/appointments.html", context)

def appointment_detail(request, appointment_id):
    doctor = get_object_or_404(doctor_models.Doctor, user=request.user)
    appointment = get_object_or_404(base_models.Appointment, appointment_id=appointment_id, doctor=doctor)


    prescriptions = base_models.Prescription.objects.filter(appointment=appointment)

    context = {
        "appointment": appointment,

        "prescriptions": prescriptions,
    }

    return render(request, "doctor/appointment_detail.html", context)

@login_required
def cancel_appointment(request, appointment_id):
    doctor = request.user.doctor
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id, doctor=doctor)

    if request.method == "POST":
        appointment.status = "Cancelled"
        appointment.save()
        messages.success(request, "Appointment has been cancelled.")
    
    return redirect('doctor:appointment_detail', appointment_id=appointment_id)

def view_prescription(request, prescription_id):
      prescription = get_object_or_404(Prescription, id=prescription_id)
      return render(request, 'doctor/prescription_detail.html', {'prescription': prescription})

@login_required
def activate_appointment(request, appointment_id):
    doctor = doctor_models.Doctor.objects.get(user=request.user)
    appointment = base_models.Appointment.objects.get(appointment_id=appointment_id, doctor=doctor)

    appointment.status = "Scheduled"
    appointment.save()

    messages.success(request, "Appointment Re-Scheduled Successfully")
    return redirect("doctor:appointment_detail", appointment.appointment_id)


@login_required
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)

    # Ensure only the doctor who owns the appointment can complete it
    if appointment.doctor.user != request.user:
        messages.error(request, "You are not authorized to complete this appointment.")
        return redirect("doctor:appointments")

    if request.method == "POST":
        if appointment.status != "Completed":
            appointment.status = "Completed"
            appointment.save()
            messages.success(request, "Appointment marked as completed.")
        else:
            messages.info(request, "Appointment is already completed.")

    return redirect("doctor:appointment_detail", appointment_id=appointment_id)



@login_required
def add_prescription(request, appointment_id):
    doctor = doctor_models.Doctor.objects.get(user=request.user)
    appointment = base_models.Appointment.objects.get(appointment_id=appointment_id, doctor=doctor)

    if request.method == "POST":
        medications = request.POST.get("medications")
        instructions = request.POST.get("instructions")
        prescription_id = request.POST.get("prescription_id")

        if prescription_id:  # Edit existing
            prescription = base_models.Prescription.objects.get(id=prescription_id, appointment=appointment)
            prescription.medications = medications
            prescription.instructions = instructions
            prescription.save()

            # Notification for edit
            PatientNotification.objects.create(
                patient=appointment.patient,
                appointment=appointment,
                type="Prescription Updated",
                seen=False
            )

            messages.success(request, "Prescription updated successfully.")

        else:  # Create new
            base_models.Prescription.objects.create(
                medications=medications,
                instructions=instructions,
                appointment=appointment
            )

            PatientNotification.objects.create(
                patient=appointment.patient,
                appointment=appointment,
                type="Prescription Added",
                seen=False
            )

            messages.success(request, "Prescription added successfully.")

        return redirect("doctor:appointment_detail", appointment.appointment_id)
@login_required
def delete_prescription(request, appointment_id, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id, appointment__appointment_id=appointment_id)
    prescription.delete()
    return redirect('doctor:appointment_detail', appointment_id=appointment_id)

@login_required
def edit_prescription(request, appointment_id, prescription_id):
    doctor = doctor_models.Doctor.objects.get(user=request.user)
    appointment = base_models.Appointment.objects.get(appointment_id=appointment_id, doctor=doctor)
    prescription = base_models.Prescription.objects.get(id=prescription_id, appointment=appointment)

    if request.method == "POST":
        medications = request.POST.get("medications")
        instructions = request.POST.get("instructions", "")
        prescription.medications = medications
        prescription.instructions = instructions
        prescription.save()

        PatientNotification.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            type="Prescription Updated",
            seen=False
        )

        messages.success(request, "Prescription updated successfully and patient notified.")
        return redirect("doctor:appointment_detail", appointment.appointment_id)

    # On GET: render the appointment detail template, with prescription pre-filled
    prescriptions = base_models.Prescription.objects.filter(appointment=appointment).order_by('-created_at')
    return render(request, "doctor/appointment_detail.html", {
        "appointment": appointment,
        "prescriptions": prescriptions,
        "edit_prescription": prescription,
        "editing": True
    })

@login_required
def notifications(request):
    doctor = doctor_models.Doctor.objects.get(user=request.user)

    # Get all notifications for this doctor, ordered by date (latest first)
    all_notifications = doctor_models.Notification.objects.filter(
        doctor=doctor
    ).order_by('-date')

    # Apply pagination (5 per page)
    paginator = Paginator(all_notifications, 5)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)

    context = {
        "notifications": notifications
    }

    return render(request, "doctor/notifications.html", context)


from django.urls import reverse

@login_required
def mark_noti_seen(request, id):
    doctor = doctor_models.Doctor.objects.get(user=request.user)
    notification = get_object_or_404(doctor_models.Notification, id=id, appointment__doctor=doctor)

    notification.seen = True
    notification.save()

    page = request.GET.get("page", "1")
    return redirect(f"{reverse('doctor:notifications')}?page={page}")
 

@login_required
def profile(request):
    doctor = doctor_models.Doctor.objects.get(user=request.user)
    formatted_next_available_appointment_date = doctor.next_available_appointment_date.strftime('%Y-%m-%d')
    
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        image = request.FILES.get("image")
        mobile = request.POST.get("mobile")
        country = request.POST.get("country")
        bio = request.POST.get("bio")
        specialization = request.POST.get("specialization")
        qualifications = request.POST.get("qualifications")
        years_of_experience = request.POST.get("years_of_experience")
        next_available_appointment_date = request.POST.get("next_available_appointment_date")

        doctor.full_name = full_name
        doctor.mobile = mobile
        doctor.country = country
        doctor.bio = bio
        doctor.specialization = specialization
        doctor.qualifications = qualifications
        doctor.years_of_experience = years_of_experience
        doctor.next_available_appointment_date = next_available_appointment_date

        if image != None:
            doctor.image = image

        doctor.save()
        messages.success(request, "Profile updated successfully")
        return redirect("doctor:profile")

    context = {
        "doctor": doctor,
        "formatted_next_available_appointment_date": formatted_next_available_appointment_date,
    }

    return render(request, "doctor/profile.html", context)
