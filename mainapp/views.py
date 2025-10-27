import os
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

# Create your views here.

def app(request):
    return render(request, 'main.html')

# Load model once
MODEL_FILENAME = "brain_tumor_vgg16_model.h5"
MODEL_PATH = os.path.join(settings.BASE_DIR, "models", MODEL_FILENAME)
model = load_model(MODEL_PATH)

# Binary classification
CLASS_LABELS = ['No Tumor', 'Tumor']

def mri_classification_view(request):
    if request.method == "POST" and request.FILES.get("mri_image"):
        mri_file = request.FILES["mri_image"]

        # Save uploaded file temporarily
        temp_path = default_storage.save(f"temp/{mri_file.name}", mri_file)
        temp_file_full_path = os.path.join(settings.MEDIA_ROOT, temp_path)

        try:
            # Preprocess image
            img = load_img(temp_file_full_path, target_size=(224, 224))
            img_array = img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.0

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
            pass  # Optional: delete temp files later

    # GET request
    return render(request, "mri_classification.html")
