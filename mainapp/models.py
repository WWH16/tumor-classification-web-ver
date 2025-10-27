from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class MRIClassification(models.Model):
    full_name = models.CharField(max_length=150)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    history = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    predicted_class = models.CharField(max_length=100)
    confidence = models.FloatField()
    image = models.ImageField(upload_to='mri_uploads/')
    date_uploaded = models.DateTimeField(auto_now_add=True)

    process_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='processed_mris'
    )

    def __str__(self):
        return f"{self.full_name} - {self.predicted_class}"