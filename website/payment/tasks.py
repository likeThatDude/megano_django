import os
from datetime import datetime
from email.mime.image import MIMEImage

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from website.settings import BASE_DIR
from website.settings import EMAIL_HOST_USER
from website.settings import HTTP_PROTOCOL
from website.settings import SERVER_DOMAIN


@shared_task
def send_html_email(login: str, email: str):
    """
    Отправляет HTML-письмо пользователю с благодарностью за покупку.

    Эта задача принимает логин пользователя и отправляет ему электронное письмо,
    содержащее информацию о покупке. Письмо включает в себя HTML-контент и
    изображения, прикрепленные с использованием Content-ID.

    Параметры:
        login (str): Логин пользователя, которому отправляется письмо.
        email (str): Email который пользователь вписал при оплате товара.

    Возвращает:
        None: Функция не возвращает никаких значений.
    """

    subject = "Спасибо за покупку !"
    from_email = EMAIL_HOST_USER
    to_email = email
    http_protocol = HTTP_PROTOCOL

    context = {
        "username": login,
        "year": datetime.now().year,
        "domain": SERVER_DOMAIN,
        "order_id": 8,
        "email": from_email,
        "protocol": HTTP_PROTOCOL,
    }

    html_content = render_to_string("payment/email_payment.html", context)
    plain_message = "Это текстовая версия вашего письма."

    email = EmailMultiAlternatives(subject, plain_message, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")

    attach_image(email, "logo.png", "image1", "static/assets/img/logo.png")
    attach_image(email, "support_email.gif", "gif_support", "static/assets/img/support_email.gif")
    attach_image(email, "dog_courier.gif", "dog_support", "static/assets/img/dog_courier.gif")

    try:
        email.send()
        print("Письмо успешно отправлено.")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


def attach_image(email, filename: str, content_id: str, file_path: str):
    """
    Прикрепляет изображение к письму с использованием Content-ID.

    Эта функция читает изображение из указанного пути и прикрепляет его к
    объекту письма с заданным Content-ID. Изображение может быть использовано
    в HTML-контенте письма.

    Параметры:
        email (EmailMultiAlternatives): Объект письма, к которому будет прикреплено изображение.
        filename (str): Имя файла изображения.
        content_id (str): Content-ID для привязки изображения в HTML-коде.
        file_path (str): Путь к файлу изображения относительно BASE_DIR.

    Возвращает:
        None: Функция не возвращает никаких значений.

    Исключения:
        FileNotFoundError: Если указанный файл не найден по заданному пути.
        IOError: Если произошла ошибка при чтении файла.
    """

    file_full_path = os.path.join(BASE_DIR, file_path)

    try:
        if not os.path.exists(file_full_path):
            raise FileNotFoundError(f"Файл не найден: {file_full_path}")

        with open(file_full_path, "rb") as img:
            image = MIMEImage(img.read())
            image.add_header("Content-ID", f"<{content_id}>")
            image.add_header("Content-Disposition", "inline", filename=filename)

            email.attach(image)

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except IOError as e:
        print(f"Ошибка при чтении файла {file_full_path}: {e}")
    except Exception as e:
        print(f"Возникла непредвиденная ошибка: {e}")
