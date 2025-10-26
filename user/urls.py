from django.urls import path

from .views import login_view, signup_view

urlpatterns = [
    path('', login_view, name='login_view'),
    path('signup/', signup_view, name='signup_view'),
]
