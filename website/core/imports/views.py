import logging
import os

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.shortcuts import render

from .tasks import import_products_task

# Создание директории для логов
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Настройка логирования
logging.basicConfig(filename=os.path.join(log_directory, "import.log"), level=logging.INFO)

# Создание директории для загрузок
upload_directory = "uploads"
if not os.path.exists(upload_directory):
    os.makedirs(upload_directory)


def import_products_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        files = request.FILES.getlist("files")
        if not files:
            files = [f for f in os.listdir(upload_directory) if f.endswith((".json", ".xml"))]

        for file in files:
            file_path = os.path.join(upload_directory, file.name)
            with open(file_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            import_products_task.delay(file_path, email)

        return redirect("success")

    return render(request, "core/import.html")


