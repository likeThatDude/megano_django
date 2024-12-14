import os

from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import QuerySet
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage

from catalog.models import Product
from custom_auth.models import CustomUser
from discount.models import Discount
from website.celery import app
from website.settings import EMAIL_HOST_USER
from website.settings import HTTP_PROTOCOL
from website.settings import SERVER_DOMAIN


@app.task
def send_three_random_discount_category_friday():
    """
    Отправляем электронное письмо с HTML-контентом

    Запланированная задача исполняется каждую пятницу в 14:00 ч. по МСК.
    Выбираем 3 рандомных товара по скидке. Письмо включает в себя HTML-контент и
    изображения, прикрепленные с использованием Content-ID.

    Возвращает:
        None: Функция не возвращает никаких значений.

    """
    subject = "Пятничные скидки"
    http_protocol = HTTP_PROTOCOL
    from_email = EMAIL_HOST_USER
    users: QuerySet[CustomUser] = CustomUser.objects.all()

    for user in users:
        try:
            products: set[Product] = set(Discount.get_discounted_products(3))

            html_content = render_to_string(
                "discount/discount_email.html",
                {
                    "username": user.login,
                    "products": products,
                    "protocol": http_protocol,
                    "domain": SERVER_DOMAIN,
                    "year": datetime.now().year,
                    "email": from_email,
                }
            )

            plain_message = strip_tags(html_content)
            email: EmailMultiAlternatives = EmailMultiAlternatives(
                subject,
                plain_message,
                from_email,
                [user.email]
            )
            email.attach_alternative(html_content, "text/html")

            attach_images(email, products, "image")

            try:
                email.send()
                print("Письмо успешно отправлено.")

            except Exception as error:
                print(f"Ошибка при отправке письма: {error}")

        except Exception as error:
            print(f"Произошла ошибка! | Error: {error}")
            pass


def attach_images(email, products: set[Product], cid: str = "image"):
    """
    Прикрепляем изображения к электронному письму с использованием Content-ID.

    Эта функция читает изображение по указанному пути и прикрепляет его к
    объекту письма с заданным Content-ID. Изображение может быть использовано
    в HTML-контенте письма.

    Параметры:
        email (EmailMultiAlternatives): Объект письма, к которому будет прикреплено изображение.
        products (set[Products]): товары, на которые действует скидка
        cid (str): Content-ID для привязки изображения в HTML-коде.

    Возвращает:
        None: Функция не возвращает никаких значений.

    """
    for index, product in enumerate(products, start=1):

        file_full_path = settings.MEDIA_ROOT / product.preview.name
        filename: str = file_full_path.name
        content_id: str = f"{cid}_{index}"

        try:
            if not os.path.exists(file_full_path):
                raise FileNotFoundError(f"Файл не найден: {file_full_path}")

            with open(file_full_path, "rb") as img:
                image = MIMEImage(img.read())
                image.add_header("Content-ID", f"<{content_id}>")
                image.add_header("Content-Disposition", "inline", filename=filename)

                email.attach(image)

        except FileNotFoundError as error:
            print(f"Файл не был найден | Error: {error}")

        except IOError as error:
            print(f"Ошибка при чтении файла {file_full_path} | Error: {error}")

        except Exception as error:
            print(f"Произошла ошибка | Error: {error}")
