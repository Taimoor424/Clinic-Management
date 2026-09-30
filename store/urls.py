from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.store_home, name='store_home'),
    path('medicine/<int:medicine_id>/', views.medicine_detail, name='medicine_detail'),

]