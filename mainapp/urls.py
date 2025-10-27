from django.urls import path
from .views import app, mri_classification_view

urlpatterns = [
    path('', app, name='app'),
]

