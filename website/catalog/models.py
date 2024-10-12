from django.db import models


class Category(models.Model):
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        db_table = "Category"
        ordering = ("name",)

    name = models.CharField(max_length=50, unique=True)
    icon = models.FileField(
        upload_to="assets/img/icons/departments",
        null=True,
        blank=True,
    )
    archived = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
