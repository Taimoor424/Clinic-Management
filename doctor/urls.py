from django.urls import path

from doctor import views

app_name = "doctor"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("appointments/", views.appointments, name="appointments"),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path("cancel_appointment/<appointment_id>/", views.cancel_appointment, name="cancel_appointment"),
    path("activate_appointment/<appointment_id>/", views.activate_appointment, name="activate_appointment"),
    path("complete_appointment/<appointment_id>/", views.complete_appointment, name="complete_appointment"),
    path('appointments/<str:appointment_id>/prescription/<int:prescription_id>/delete/',views.delete_prescription, name='delete_prescription' ),
    path("add_prescription/<appointment_id>/", views.add_prescription, name="add_prescription"),
    path('appointment/<str:appointment_id>/prescription/<int:prescription_id>/edit/', views.edit_prescription, name='edit_prescription'),
    path("notifications/", views.notifications, name="notifications"),
    path('doctor/mark_noti_seen/<int:id>/', views.mark_noti_seen, name='mark_noti_seen'),
    path("profile/", views.profile, name="profile"),

]