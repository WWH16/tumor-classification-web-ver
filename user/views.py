from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import SignupForm, LoginForm

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SignupForm
from .models import UserProfile

def landing_page(request):
    return render(request, "index.html")

def signup_view(request):
    employee_id_error = None
    email_error = None
    password_error = None

    if request.method == "POST":
        form = SignupForm(request.POST)
        employee_id = request.POST.get("employee_id", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        has_error = False

        # Password match check
        if password1 != password2:
            password_error = "Passwords do not match."
            has_error = True

        # Employee ID uniqueness
        if UserProfile.objects.filter(employee_id=employee_id).exists():
            employee_id_error = "Employee ID already exists."
            has_error = True

        # Email uniqueness
        if User.objects.filter(email=email).exists():
            email_error = "Email is already registered."
            has_error = True

        # Create user if no errors
        if not has_error:
            user = User.objects.create_user(
                username=employee_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password1
            )
            UserProfile.objects.create(user=user, employee_id=employee_id)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login_view")
    else:
        form = SignupForm()

    return render(request, "signup.html", {
        "form": form,
        "employee_id_error": employee_id_error,
        "email_error": email_error,
        "password_error": password_error
    })


def login_view(request):
    login_error = None

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data["employee_id"]
            password = form.cleaned_data["password"]

            try:
                profile = UserProfile.objects.get(employee_id=employee_id)
                user = authenticate(request, username=profile.user.username, password=password)

                if user is not None:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    return redirect("/app")
                else:
                    login_error = "Invalid credentials."
            except UserProfile.DoesNotExist:
                login_error = "Invalid credentials."
        else:
            login_error = "Invalid credentials."
    else:
        form = LoginForm()

    return render(request, "login.html", {
        "form": form,
        "login_error": login_error
    })


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("login_view")