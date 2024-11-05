import json
import logging
import os
import shutil
import xml.etree.ElementTree as ET

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(bind=True)
def import_products_task(self, file_path, email):
    logging.info(f"Начинаем импорт для {file_path}")

    errors = []
    products_imported = []

    try:
        if file_path.endswith(".json"):
            with open(file_path) as f:
                data = json.load(f)
                for item in data.get("products", []):
                    try:
                        products_imported.append(item)
                    except Exception as e:
                        errors.append(f"Не удалось импортировать продукт {item['id']}: {str(e)}")

        elif file_path.endswith(".xml"):
            tree = ET.parse(file_path)
            root = tree.getroot()
            for item in root.findall("product"):
                try:
                    products_imported.append(item)
                except Exception as e:
                    errors.append(f"Не удалось импортировать продукт {item.find('id').text}: {str(e)}")

        # Перемещение файла в processed директорию
        processed_dir = "processed"
        os.makedirs(processed_dir, exist_ok=True)

        if errors:
            shutil.move(file_path, os.path.join(processed_dir, "failed", os.path.basename(file_path)))
            log_message = f"Импортировано: {len(products_imported)} товаров. Ошибки: {len(errors)}"
            logging.info(log_message)
            send_email_notification(email, log_message, errors)
        else:
            shutil.move(file_path, os.path.join(processed_dir, "success", os.path.basename(file_path)))
            logging.info(f"Успешно импортировано {len(products_imported)} товаров.")

    except Exception as e:
        logging.error(f"Критическая ошибка при импорте: {str(e)}")
        self.retry(exc=e)


def send_email_notification(email, message, errors):
    subject = "Содержание"
    body = f"{message}Ошибки: {errors}"
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])
