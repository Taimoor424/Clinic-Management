from django.urls import path, include
from base import views

app_name= 'base'

urlpatterns= [

    path('', views.index, name='home'), 
    path('about/', views.about, name='about'),
    path('auth/sign-in/about/', views.about, name='home '),
    path('', include('userauths.urls')),
    path('services/', views.services, name='service'),
    path('doctors/', views.doctors_list, name='doctors'),
    path('blogs/', views.blogs, name='blogs'),
    path('blogs/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('', views.index, name='testimonial'),
    path('', views.index, name='team'),
    path('', views.index, name='appointment'),
    path('contact/', views.contact_view, name='contact_view'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('book_appointment/<int:service_id>/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('symptom-checker/', views.symptom_checker, name='symptom_checker'),


]