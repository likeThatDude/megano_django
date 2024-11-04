from account.models import CustomUser
from django.http import HttpRequest


def user_is_auth(request: HttpRequest):
    user = CustomUser.objects.filter(pk=request.user.pk)
    return {"user_is_auth": True if user else False}
