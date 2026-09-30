# forms.py

from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message', 'rows': 5}),
        }

class AppointmentForm(forms.Form):
    full_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    mobile = forms.CharField(required=True)
    gender = forms.ChoiceField(choices=[("Male", "Male"), ("Female", "Female")], required=True)
    issues = forms.CharField(widget=forms.Textarea, required=True)

