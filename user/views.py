from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import SignupForm, LoginForm

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data["employee_id"]
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]

            # ✅ Password match check
            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                return render(request, "signup.html", {"form": form})

            # ✅ Check for duplicate employee ID
            if UserProfile.objects.filter(employee_id=employee_id).exists():
                messages.error(request, "Employee ID already exists.")
                return render(request, "signup.html", {"form": form})

            # ✅ Create new user
            user = User.objects.create_user(
                username=employee_id,  # Use employee_id as internal username
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password1
            )

            # ✅ Create linked profile
            UserProfile.objects.create(user=user, employee_id=employee_id)

            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login_view")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data["employee_id"]
            password = form.cleaned_data["password"]

            try:
                # ✅ Authenticate using linked User object
                profile = UserProfile.objects.get(employee_id=employee_id)
                user = authenticate(request, username=profile.user.username, password=password)

                if user is not None:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    return redirect("/app")  # Use your actual dashboard URL name
                else:
                    messages.error(request, "Invalid employee ID or password.")
            except UserProfile.DoesNotExist:
                messages.error(request, "Employee ID not found.")
        else:
            messages.error(request, "Please fill in all required fields.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("login_view")
