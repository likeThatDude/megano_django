from celery import shared_task
from datetime import timedelta
from django.conf import settings
from django.db.models import QuerySet
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.utils.timezone import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


from custom_auth.models import CustomUser
from order.models import Order
from website.celery import app
from website.settings import EMAIL_HOST_USER
from website.settings import HTTP_PROTOCOL
from website.settings import SERVER_DOMAIN


@shared_task(
    bind=True,
    name="email_notification_in_2_days_register"
)
def notify_user_after_register(self, user_pk):
    """
    Запланированная задача рассылки электронных писем
    после регистрации пользователя. Текст сообщения зависит от того,
    совершил ли пользователь заказ в течение двух дней или нет.

    Атрибуты:
        user_pk - первичный ключ пользователя в базе данных

    """
    subject: str = f"Обратная связь"

    try:
        user = CustomUser.objects.get(pk=user_pk)
        user_orders: QuerySet[Order] = user.orders.all()
        registration_date = user.created_at
        start_date, end_date = (
            registration_date,
            registration_date + timedelta(days=2)
        )
        recently_orders: QuerySet[Order] = user_orders.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        )
        start_message: str = (f"{user.profile.first_name}, приветсвую! "
                              f"Это онлайн-магазин MEGANO. Вы зарегистрировались на нашей платформе позавчера. ")

        if recently_orders.exists():
            message: str = (f"Видим что вы оформили заказ на нашем сайте. "
                       f"Хотели узнать, всё ли Вам было понятно при оформлении или есть что-то, "
                       f"что мы со своей стороны могли бы улучшить?")
        else:
            message: str = (f"Видим, что вы еще пока не оформили ни одного заказа. "
                       f"Подскажите, если ли какие то замечания по работе нашей платформы или пока всё понятно?")

        message: str = start_message + message
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True
        )

    except Exception as error:
        print(f"Не удалось выполнить задачу notify_user_after_register")
        raise self.retry(exc=error)


@app.task
def send_user_happy_birthday():
    """
    Запланированная задача отправки поздравления с днем рождения пользователю
    Проверка производится каждый день.
    Если у пользователя день рождение, отправляем электронное письмо

    """
    subject: str = "С днем рождения от MEGANO"
    from_email = EMAIL_HOST_USER
    users: QuerySet[CustomUser] = CustomUser.objects.all()

    for user in users:
        try:
            current_date = datetime.today().date()

            if user.birthday == current_date:
                html_content = render_to_string(
                    "custom_auth/happy_birthday_email.html",
                    {
                        "username": user.login,
                        "company": "MEGANO",
                        "protocol": HTTP_PROTOCOL,
                        "domain": SERVER_DOMAIN,
                        "year": datetime.now().year,
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

                try:
                    email.send()
                    print("Письмо успешно отправлено.")

                except Exception as error:
                    print(f"Ошибка при отправке письма: {error}")

        except Exception as error:
            print(f"Произошла ошибка! | Error: {error}")
