from django.http import HttpRequest

from account.models import CustomUser


def user_is_auth(request: HttpRequest):
    user = CustomUser.objects.filter(pk=request.user.pk)
    return {"user_is_auth": True if user else False}
