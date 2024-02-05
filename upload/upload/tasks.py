from celery import shared_task
from files.models import File
import os
from django.conf import settings
from rest_framework import status
import mimetypes
from PIL import Image



@shared_task
def process_file(file_id=None):
    try:
        file = File.objects.get(pk=file_id)
        file_path = settings.MEDIA_ROOT / file.file.name

        if not os.path.exists(file_path):
            return {"error": "File does not exist", "status_code": status.HTTP_400_BAD_REQUEST}

        file_type, _ = mimetypes.guess_type(file_path)

        if file_type and file_type.startswith("image"):
            image = Image.open(file_path)
            image.thumbnail((150, 150))
            image.save(file_path)

        elif file_type and file_type.startswith("text"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            updated_text = text.replace("ё", "е").replace('Ё', 'Е')

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_text)

        else:
            file.processed = True
            file.save()

        file.processed = True
        file.save()

    except File.DoesNotExist:
        return {"error": "File not found", "status_code": status.HTTP_400_BAD_REQUEST}