import os
import cv2
import numpy as np
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Avg, Max, Count
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from tensorflow.keras.models import load_model
from .models import MRIClassification

# Load the trained model once at startup
MODEL_FILENAME = "brain_tumor_vgg16_model.h5"
MODEL_PATH = os.path.join(settings.BASE_DIR, "models", MODEL_FILENAME)
model = load_model(MODEL_PATH)

CLASS_LABELS = ['No Tumor', 'Tumor']


def app(request):
    return render(request, 'main.html')


@login_required
def mri_classification_view(request):
    if request.method == "POST":
        # Check if an image was uploaded
        if "image" not in request.FILES:
            return JsonResponse({"success": False, "error": "No MRI file received."})

        # === Save uploaded image to MEDIA_ROOT/temp/ ===
        mri_file = request.FILES["image"]
        file_path = default_storage.save(f"temp/{mri_file.name}", mri_file)
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # === Preprocess image for model ===
        img = cv2.imread(full_file_path)
        img_resized = cv2.resize(img, (224, 224))
        img_resized = np.expand_dims(img_resized, axis=0)

        # === Predict ===
        preds = model.predict(img_resized)
        predicted_index = np.argmax(preds, axis=1)[0]
        predicted_class = CLASS_LABELS[predicted_index]
        confidence = float(np.max(preds))

        # === Save classification record ===
        record = MRIClassification.objects.create(
            full_name=request.POST.get("full_name", "Unknown"),
            age=request.POST.get("age", 0),
            sex=request.POST.get("sex", "Unknown"),
            history=request.POST.get("history", ""),
            notes=request.POST.get("notes", ""),
            predicted_class=predicted_class,
            confidence=confidence,
            image=file_path,
            process_by=request.user,
        )

        return JsonResponse({
            "success": True,
            "id": record.id,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "image_url": record.image.url,
        })

    return JsonResponse({"success": False, "error": "Invalid request method."})


def history(request):
    # Get only current user's classifications
    classifications = MRIClassification.objects.filter(process_by=request.user)

    # Get total count before filtering
    total_count = classifications.count()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        classifications = classifications.filter(
            Q(full_name__icontains=search_query) |
            Q(predicted_class__icontains=search_query) |
            Q(notes__icontains=search_query) |
            Q(history__icontains=search_query)
        )

    # Diagnosis filter
    diagnosis_filter = request.GET.get('diagnosis', '')
    if diagnosis_filter:
        classifications = classifications.filter(predicted_class=diagnosis_filter)

    # Sex filter
    sex_filter = request.GET.get('sex', '')
    if sex_filter:
        classifications = classifications.filter(sex=sex_filter)

    # Date range filter
    date_range = request.GET.get('date_range', '')
    if date_range:
        today = datetime.now()
        if date_range == 'today':
            start_date = today.replace(hour=0, minute=0, second=0)
            classifications = classifications.filter(date_uploaded__gte=start_date)
        elif date_range == 'week':
            start_date = today - timedelta(days=7)
            classifications = classifications.filter(date_uploaded__gte=start_date)
        elif date_range == 'month':
            start_date = today - timedelta(days=30)
            classifications = classifications.filter(date_uploaded__gte=start_date)
        elif date_range == 'year':
            start_date = today - timedelta(days=365)
            classifications = classifications.filter(date_uploaded__gte=start_date)

    # Sorting
    sort_by = request.GET.get('sort', '-date_uploaded')
    classifications = classifications.order_by(sort_by)

    # Get unique values for filters
    all_diagnoses = MRIClassification.objects.values_list('predicted_class', flat=True).distinct()
    all_sexes = MRIClassification.objects.values_list('sex', flat=True).distinct()

    # Pagination
    paginator = Paginator(classifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Compute average confidence for current user only
    avg_conf = classifications.aggregate(avg_confidence=Avg('confidence'))['avg_confidence'] or 0
    avg_confidence = avg_conf * 100

    context = {
        'page_obj': page_obj,
        'total_count': total_count,
        'search_query': search_query,
        'diagnosis_filter': diagnosis_filter,
        'sex_filter': sex_filter,
        'date_range': date_range,
        'sort_by': sort_by,
        'all_diagnoses': all_diagnoses,
        'all_sexes': all_sexes,
        'avg_confidence': avg_confidence,
    }

    return render(request, 'history.html', context)


@login_required
def history_detail_view(request, pk):
    classification = get_object_or_404(
        MRIClassification,
        pk=pk,
        process_by=request.user
    )
    return render(request, 'history_detail.html', {'classification': classification})


@login_required
def history_edit_view(request, pk):
    classification = get_object_or_404(
        MRIClassification,
        pk=pk,
        process_by=request.user
    )

    success = False

    if request.method == 'POST':
        classification.full_name = request.POST.get('full_name')
        classification.age = request.POST.get('age')
        classification.sex = request.POST.get('sex')
        classification.history = request.POST.get('history')
        classification.notes = request.POST.get('notes')
        classification.save()
        success = True

    # Prepare display-ready confidence percent
    raw_conf = classification.confidence if classification.confidence is not None else 0.0
    try:
        raw_conf_f = float(raw_conf)
    except (TypeError, ValueError):
        raw_conf_f = 0.0

    if raw_conf_f <= 1:
        confidence_percent = round(raw_conf_f * 100, 2)
    else:
        confidence_percent = round(raw_conf_f, 2)

    return render(request, 'history_edit.html', {
        'classification': classification,
        'confidence_percent': confidence_percent,
        'success': success,
    })


@login_required
@csrf_exempt
def history_delete_view(request, pk):
    if request.method == 'POST':
        classification = get_object_or_404(
            MRIClassification,
            pk=pk,
            process_by=request.user
        )
        classification.delete()
        return JsonResponse({
            "success": True,
            "message": "Record deleted successfully!"
        })
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)


@login_required
def history_export_csv(request):
    """Export classification history to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mri_classifications.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Patient Name', 'Age', 'Sex',
        'Diagnosis', 'Confidence (%)', 'Date',
        'Medical History', 'Notes', 'Processed By'
    ])

    classifications = MRIClassification.objects.filter(
        process_by=request.user
    ).order_by('-date_uploaded')

    for c in classifications:
        writer.writerow([
            c.id,
            c.full_name,
            c.age,
            c.sex,
            c.predicted_class,
            f"{c.confidence:.2f}",
            c.date_uploaded.strftime('%Y-%m-%d %H:%M'),
            c.history or '',
            c.notes or '',
            c.process_by.get_full_name() if c.process_by else ''
        ])

    return response


@login_required
def history_bulk_delete(request):
    """Bulk delete multiple records"""
    if request.method == 'POST':
        ids = request.POST.getlist('record_ids')
        if ids:
            MRIClassification.objects.filter(
                pk__in=ids,
                process_by=request.user
            ).delete()
            messages.success(request, f'{len(ids)} record(s) deleted successfully!')
        else:
            messages.warning(request, 'No records selected!')
    return redirect('history')


@login_required
def history_print_view(request, pk):
    """Generate printable report or PDF for a classification"""
    classification = get_object_or_404(
        MRIClassification,
        pk=pk,
        process_by=request.user
    )
    context = {
        'classification': classification,
        'now': timezone.now()
    }
    return render(request, 'history_print.html', context)


@login_required
def dashboard_view(request):
    """Main dashboard with statistics"""
    user = request.user

    # Get date ranges
    today = timezone.now().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=7)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    # Total classifications
    total_classifications = MRIClassification.objects.filter(
        process_by=user
    ).count()

    # This month
    month_classifications = MRIClassification.objects.filter(
        process_by=user,
        date_uploaded__gte=month_start
    ).count()

    # Last month for comparison
    last_month_classifications = MRIClassification.objects.filter(
        process_by=user,
        date_uploaded__gte=last_month_start,
        date_uploaded__lt=month_start
    ).count()

    # Calculate month change percentage
    if last_month_classifications > 0:
        month_change = ((month_classifications - last_month_classifications) /
                        last_month_classifications * 100)
    else:
        month_change = 100 if month_classifications > 0 else 0

    # This week
    week_classifications = MRIClassification.objects.filter(
        process_by=user,
        date_uploaded__gte=week_start
    ).count()

    # Robust average confidence
    agg = MRIClassification.objects.filter(process_by=user).aggregate(
        avg_conf=Avg('confidence'),
        max_conf=Max('confidence'),
    )
    avg_conf = agg.get('avg_conf') or 0
    max_conf = agg.get('max_conf') or 0

    if max_conf <= 1:
        avg_percentage = avg_conf * 100
    else:
        avg_percentage = avg_conf

    avg_confidence = round(float(avg_percentage), 1)

    # Diagnosis distribution
    diagnosis_stats = MRIClassification.objects.filter(
        process_by=user
    ).values('predicted_class').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    # Calculate percentages
    for stat in diagnosis_stats:
        stat['percentage'] = (stat['count'] / total_classifications * 100) if total_classifications > 0 else 0

    # Recent classifications
    recent_classifications = MRIClassification.objects.filter(
        process_by=user
    ).order_by('-date_uploaded')[:5]

    # Daily activity for last 30 days
    thirty_days_ago = today - timedelta(days=29)
    daily_counts = {(thirty_days_ago + timedelta(days=i)): 0 for i in range(30)}

    activities = MRIClassification.objects.filter(
        process_by=user,
        date_uploaded__gte=thirty_days_ago
    ).values('date_uploaded__date').annotate(count=Count('id'))

    for activity in activities:
        daily_counts[activity['date_uploaded__date']] = activity['count']

    # Prepare daily activity data
    max_count = max(daily_counts.values()) if daily_counts else 1
    daily_activity = []
    for date, count in sorted(daily_counts.items()):
        height = (count / max_count * 100) if max_count > 0 else 0
        daily_activity.append({
            'date': date,
            'count': count,
            'height': height
        })

    context = {
        'total_classifications': total_classifications,
        'month_classifications': month_classifications,
        'month_change': round(month_change, 1),
        'week_classifications': week_classifications,
        'avg_confidence': avg_confidence,
        'diagnosis_stats': diagnosis_stats,
        'recent_classifications': recent_classifications,
        'daily_activity': daily_activity,
    }

    return render(request, 'dashboard.html', context)