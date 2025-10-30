from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class MRIClassification(models.Model):
    full_name = models.CharField(max_length=150)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    history = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    predicted_class = models.CharField(max_length=100)
    confidence = models.FloatField()
    image = models.ImageField(upload_to='temp/')
    date_uploaded = models.DateTimeField(auto_now_add=True)

    process_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='processed_mris'
    )

    class Meta:
        ordering = ['-date_uploaded']
        verbose_name = 'MRI Classification'
        verbose_name_plural = 'MRI Classifications'

    def __str__(self):
        return f"{self.full_name} - {self.predicted_class}"

    @property
    def confidence_percentage(self):
        """Returns confidence as a percentage (0-100)"""
        value = self.confidence * 100 if self.confidence <= 1 else self.confidence
        return round(value, 2)

    @property
    def confidence_percentage_int(self):
        """Returns confidence as integer percentage (truncated)"""
        value = self.confidence * 100 if self.confidence <= 1 else self.confidence
        return int(value)

    @property
    def confidence_level(self):
        """Returns confidence level category"""
        conf = self.confidence_percentage
        if conf >= 90:
            return 'excellent'
        elif conf >= 75:
            return 'high'
        elif conf >= 60:
            return 'moderate'
        elif conf >= 40:
            return 'low'
        else:
            return 'very-low'

    @property
    def confidence_color(self):
        """Returns color based on confidence level"""
        level = self.confidence_level
        colors = {
            'excellent': '#059669',  # emerald-600
            'high': '#16a34a',  # green-600
            'moderate': '#f59e0b',  # amber-500
            'low': '#f97316',  # orange-500
            'very-low': '#dc2626'  # red-600
        }
        return colors.get(level, '#6b7280')