from django.contrib import admin
from base import models
from import_export.admin import ImportExportModelAdmin
from base.models import Contact
from base.models import Blog,BlogCategory
from .models import Appointment


class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'is_published']
    list_filter = ['category', 'is_published']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}

class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'message', 'created_at']



class AppointmentInline(admin.TabularInline):
    model = models.Appointment
    extra = 1




class PrescriptionInline(admin.TabularInline):
    model = models.Prescription
    extra = 1



class ServiceAdmin(ImportExportModelAdmin):
    list_display = ['name', 'cost']
    search_fields = ['name', 'description']
    filter_horizontal = ['available_doctors']

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'patient', 'doctor', 'appointment_date', 'status']
    search_fields = [
        'appointment_id',
        'patient__user__first_name',
        'patient__user__last_name',
        'doctor__user__username',
    ]
    inlines = [PrescriptionInline]
    

class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'appointment']
    search_fields = ['appointment__appointment_id']

    def appointment_id(self, obj):
        return obj.appointment.appointment_id
    appointment_id.short_description = 'Appointment ID'
    

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['name', 'publish_date']
    search_fields = ['name', 'content']


admin.site.register(models.Service, ServiceAdmin)
admin.site.register(models.Appointment, AppointmentAdmin)
admin.site.register(models.Prescription, PrescriptionAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Blog, BlogAdmin)
