from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from base import models as base_models
from patient import models as patient_models
from patient.models import Patient
from cart.models import Order
from base.models import Appointment 
from patient.models import Patient, Notification
from django.core.paginator import Paginator


@login_required
def my_orders(request):
    patient = request.user.patient
    orders = Order.objects.filter(patient=patient).order_by('-created_at')
    return render(request, 'patient/my_orders.html', {'orders': orders})

@login_required
def dashboard(request):
    patient = get_object_or_404(Patient, user=request.user)

    appointments = Appointment.objects.filter(patient=patient)
    active_appointment_count = appointments.exclude(status="Cancelled").count()

    notifications = Notification.objects.filter(patient=patient, seen=False)
    orders = Order.objects.filter(patient=patient).order_by('-created_at')
    
    context = {
        'appointments': appointments,
        'notifications': notifications,
        'orders': orders,
        'active_appointment_count': active_appointment_count,  
    }

    return render(request, "patient/dashboard.html", context)



@login_required
def appointments(request):
    patient = patient_models.Patient.objects.get(user=request.user)
    search_query = request.GET.get('search', '')  

    appointments = base_models.Appointment.objects.filter(patient=patient)

    if search_query:
        appointments = appointments.filter(
            doctor__full_name__icontains=search_query
            
        )

    context = {
        "appointments": appointments,
        "search_query": search_query,
    }

    return render(request, "patient/appointments.html", context)

@login_required
def appointment_detail(request, appointment_id):
    patient = patient_models.Patient.objects.get(user=request.user)
    appointment = base_models.Appointment.objects.get(appointment_id=appointment_id, patient=patient)
    
   
    prescriptions = base_models.Prescription.objects.filter(appointment=appointment)

    context = {
        "appointment": appointment,
        
        "prescriptions": prescriptions,
    }

    return render(request, "patient/appointment_detail.html", context)




@login_required
def cancel_appointment(request, appointment_id):
    patient = patient_models.Patient.objects.get(user=request.user)
    appointment = base_models.Appointment.objects.get(appointment_id=appointment_id, patient=patient)

    appointment.status = "Cancelled"
    appointment.save()

    messages.success(request, "Appointment Cancelled Successfully")
    return redirect("patient:appointment_detail", appointment.appointment_id)


@login_required
def activate_appointment(request, appointment_id):
    patient = patient_models.Patient.objects.get(user=request.user)
    appointment = base_models.Appointment.objects.get(appointment_id=appointment_id, patient=patient)

    appointment.status = "Scheduled"
    appointment.save()

    messages.success(request, "Appointment Re-Scheduled Successfully")
    return redirect("patient:appointment_detail", appointment.appointment_id)


@login_required
def complete_appointment(request, appointment_id):
    patient = patient_models.Patient.objects.get(user=request.user)
    appointment = base_models.Appointment.objects.get(appointment_id=appointment_id, patient=patient)

    appointment.status = "Completed"
    appointment.save()

    messages.success(request, "Appointment Completed Successfully")
    return redirect("patient:appointment_detail", appointment.appointment_id)


@login_required
def notifications(request):
    patient = patient_models.Patient.objects.get(user=request.user)

    # ✅ Fetch all notifications for the patient, unseen first
    notification_list = patient_models.Notification.objects.filter(
        patient=patient
    ).order_by('seen', '-date')  # unseen first, then latest

    # ✅ Paginate - 5 notifications per page
    paginator = Paginator(notification_list, 5)
    page_number = request.GET.get("page")
    notifications = paginator.get_page(page_number)

    return render(request, "patient/notifications.html", {
        "notifications": notifications
    })


from django.urls import reverse

@login_required
def mark_noti_seen(request, id):
    patient = patient_models.Patient.objects.get(user=request.user)
    notification = get_object_or_404(patient_models.Notification, patient=patient, id=id)

    notification.seen = True
    notification.save()

    page = request.GET.get("page", "1")
    return redirect(f"{reverse('patient:notifications')}?page={page}")
@login_required
def profile(request):
    patient = patient_models.Patient.objects.get(user=request.user)
    formatted_dob = patient.dob.strftime('%Y-%m-%d')
    
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        image = request.FILES.get("image")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        blood_group = request.POST.get("blood_group")

        patient.full_name = full_name
        patient.mobile = mobile
        patient.address = address
        patient.gender = gender
        patient.dob = dob
        patient.blood_group = blood_group

        if image != None:
            patient.image = image

        patient.save()
        messages.success(request, "Profile updated successfully")
        return redirect("patient:profile")

    context = {
        "patient": patient,
        "formatted_dob": formatted_dob,
    }

    return render(request, "patient/profile.html", context)



@login_required
def profile(request):
    patient = patient_models.Patient.objects.get(user=request.user)
    if patient.dob:
       formatted_dob = patient.dob.strftime("%Y-%m-%d")
    else:
       formatted_dob = "N/A"    
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        image = request.FILES.get("image")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        blood_group = request.POST.get("blood_group")

        patient.full_name = full_name
        patient.mobile = mobile
        patient.address = address
        patient.gender = gender
        patient.dob = dob
        patient.blood_group = blood_group

        if image != None:
            patient.image = image

        patient.save()
        messages.success(request, "Profile updated successfully")
        return redirect("patient:profile")

    context = {
        "patient": patient,
        "formatted_dob": formatted_dob,
    }

    return render(request, "patient/profile.html", context)
