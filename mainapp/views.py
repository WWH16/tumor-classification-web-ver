import os
import cv2
import numpy as np
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
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
        if "image" not in request.FILES:
            return JsonResponse({"success": False, "error": "No MRI file received."})

        # Save uploaded image temporarily
        mri_file = request.FILES["image"]
        file_path = default_storage.save(f"temp/{mri_file.name}", mri_file)
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # === Match GUI preprocessing ===
        img = cv2.imread(full_file_path)
        img_resized = cv2.resize(img, (224, 224))
        img_resized = np.expand_dims(img_resized, axis=0)

        # === Predict ===
        preds = model.predict(img_resized)
        predicted_index = np.argmax(preds, axis=1)[0]
        predicted_class = CLASS_LABELS[predicted_index]
        confidence = float(np.max(preds))

        # === Save record ===
        record = MRIClassification.objects.create(
            full_name=request.POST.get("full_name", "Unknown"),
            age=request.POST.get("age", 0),
            gender=request.POST.get("gender", "Unknown"),
            history=request.POST.get("history", ""),
            notes=request.POST.get("notes", ""),
            predicted_class=predicted_class,
            confidence=confidence,
            image=file_path,
            process_by=request.user,
        )

        return JsonResponse({
            "success": True,
            "predicted_class": predicted_class,
            "confidence": confidence,
        })

    return JsonResponse({"success": False, "error": "Invalid request method."})
