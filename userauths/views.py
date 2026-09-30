from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from userauths.forms import UserRegisterForm
from base.utils import send_custom_email
from userauths import forms as userauths_forms
from doctor.models import Doctor
from patient.models import Patient
from userauths import models as userauths_models
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
User = get_user_model()
def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("/")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            full_name = form.cleaned_data.get("full_name")
            email = form.cleaned_data.get("email")
            user_type = form.cleaned_data.get("user_type")

            # Save the user without logging them in
            user.save()

            # Create corresponding Doctor or Patient profile
            if user_type == "Doctor":
                Doctor.objects.create(user=user, full_name=full_name, email=email)
            else:
                Patient.objects.create(user=user, full_name=full_name, email=email)

            messages.success(request, "Account created successfully. Please log in.")
            return redirect("userauths:sign-in")  # Replace with your actual sign-in URL name

        else:
            messages.error(request, "There was an error creating your account.")
    else:
        form = UserRegisterForm()

    return render(request, "userauths/sign-up.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in")
        return redirect("/")
    
    if request.method == "POST":
        form = userauths_forms.LoginForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            try:
                user_instance = userauths_models.User.objects.get(email=email, is_active=True)
                user_authenticate = authenticate(request, email=email, password=password)

                if user_authenticate is not None:
                    login(request, user_authenticate)

                    # ✅ Send email after successful login
                    subject = "Login Notification"
                    message = f"Hello {user_instance.first_name},\n\nYou have successfully logged into your account."
                    send_custom_email(subject, message, [user_instance.email])

                    messages.success(request, "Logged in Successfully")
                    next_url = request.GET.get("next", '/')
                    return redirect(next_url)
                else:
                    messages.error(request, "Username or password does not exist!")
            except userauths_models.User.DoesNotExist:
                messages.error(request, "User does not exist!")
    else:
        form = userauths_forms.LoginForm()
    
    context = {
        "form": form
    }
    return render(request, "userauths/sign-in.html", context)

def logout_view(request):
    logout(request)
    return redirect("base:home")

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(f"/auth/reset-password/{uid}/{token}/")

            send_mail(
                "Reset your password",
                f"Click the link below to reset your password:\n\n{reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            messages.success(request, "Password reset link sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
    return render(request, "userauths/password_reset_form.html")


def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None:
        user = User.objects.get(pk=user.pk)

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, "Password has been reset. You can now log in.")
                return redirect("userauths:sign-in")
            else:
                messages.error(request, "Passwords do not match.")
        
        return render(request, "userauths/password_reset_confirm.html")
    else:
        messages.error(request, "Invalid or expired password reset link.")
        return redirect("forgot-password")