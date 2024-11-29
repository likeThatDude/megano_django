from django.core.exceptions import ValidationError
from django.db.models.fields.files import ImageFieldFile
from django.utils.translation import gettext_lazy as _


def profile_photo_directory_path(instance: "Profile", filename: str) -> str:
    """
    Генерация пути для сохранения фото/аватара пользователя
    """

    return "assets/img/profile/profile_{pk}/{filename}".format(
        pk=instance.user,
        filename=filename,
    )


def validate_avatar_size(file: ImageFieldFile):
    """
    Функция проверки допустимости (валидатор) размера изображения.
    Возвращает ValidationError, если размер превышает 2 мегабайта.
    """
    if file.size > 2 * 1024 * 1024:
        raise ValidationError(
            _("The file %(filename)s larger than 2 MB"),
            params={"filename": file.name},
        )
