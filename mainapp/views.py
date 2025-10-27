import os
import cv2
import numpy as np
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from tensorflow.keras.models import load_model

# Load model once
MODEL_FILENAME = "brain_tumor_vgg16_model.h5"
MODEL_PATH = os.path.join(settings.BASE_DIR, "models", MODEL_FILENAME)
model = load_model(MODEL_PATH)

# Binary classification
CLASS_LABELS = ['No Tumor', 'Tumor']

def app(request):
    return render(request, 'main.html')

def mri_classification_view(request):
    if request.method == "POST" and request.FILES.get("mri_image"):
        mri_file = request.FILES["mri_image"]

        # Save uploaded file temporarily
        temp_path = default_storage.save(f"temp/{mri_file.name}", mri_file)
        temp_file_full_path = os.path.join(settings.MEDIA_ROOT, temp_path)

        try:
            # Preprocess image for model (BGR 0-255, same as GUI)
            img = cv2.imread(temp_file_full_path)  # Read BGR
            img = cv2.resize(img, (224, 224))
            img_array = np.expand_dims(img, axis=0)  # Shape (1,224,224,3)
            # Note: do NOT divide by 255

            # Predict
            preds = model.predict(img_array)[0]
            top_index = np.argmax(preds)
            top_label = CLASS_LABELS[top_index]
            top_confidence = float(preds[top_index] * 100)

            # Return uploaded image URL for preview
            image_url = default_storage.url(temp_path)

            result = {
                "predicted_class": top_label,
                "confidence": top_confidence,
                "image_url": image_url
            }

            return JsonResponse({"success": True, "result": result})

        finally:
            pass  # Optionally delete temp files later

    # GET request
    return render(request, "mri_classification.html")
