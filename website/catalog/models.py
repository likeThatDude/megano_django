from django.db import models, transaction
from django.db.models import ManyToManyField, QuerySet
from django.db.models.constraints import UniqueConstraint
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from website import settings

from .utils import category_icon_directory_path
from .utils import product_image_directory_path
from .utils import product_images_directory_path
from .utils import seller_image_directory_path


class Category(models.Model):
    """
    Модель категории товара

    Attributes:
        name: название категории
        icon: иконка категории
        archived: статус архива категории
        parent_category: ссылка на родительскую категорию (если значение не NULL,
         то это подкатегория категории)
    """

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    icon = models.FileField(upload_to=category_icon_directory_path, verbose_name=_("Icon"))
    archived = models.BooleanField(default=False, verbose_name=_("Archived status"))
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_categories",
        verbose_name=_("Parent category"),
    )
    tags = models.ManyToManyField("Tag", related_name="category_tags", verbose_name=_("Сategory tags"))

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Модель тега товара
    name: название тега
    """

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        unique=True,
        db_index=True,
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = _("Tags")
        verbose_name_plural = _("Tags")
        ordering = ("name",)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Модель товара
    name: имя товара
    description: описание товара
    manufacture: производитель товара
    created_at: когда создан товар
    category: категория товара (Category)
    archived: статус архива товара
    limited_edition: статус ограниченности предложения товара
    view: статус просмотра товара
    """

    name = models.CharField(max_length=100, null=False, blank=False, db_index=True, verbose_name=_("Name"))
    description = models.TextField(null=True, blank=True, db_index=True, verbose_name=_("Description"))
    short_description = models.CharField(max_length=80, null=True, blank=True, verbose_name=_("Short description"))
    product_type = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_("Product Type"),
        null=False,
        blank=False,
    )
    manufacture = models.CharField(max_length=100, db_index=True, verbose_name=_("Manufacture"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_("PK category"),
        related_name="products",
    )
    archived = models.BooleanField(default=False, verbose_name=_("Archived status"))
    limited_edition = models.BooleanField(default=False, verbose_name=_("Limited edition"))
    views = models.PositiveBigIntegerField(default=0, verbose_name=_("Views"))
    sorting_index = models.PositiveIntegerField(default=0, verbose_name=_("Sorting Index"))
    preview = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_image_directory_path,
        verbose_name=_("Preview"),
    )
    tags = ManyToManyField(Tag, related_name="products", verbose_name=_("Tags"))

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"

    def __str__(self) -> str:
        return f"Product(id={self.pk}, name={self.name[:20]} {'...' if len(self.name) > 20 else ''})"


class ProductImage(models.Model):
    """
    Модель изображения товара
    product: ссылка на товар к которому относится фотография (Product)
    image: изображение товара
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("PK product"),
        related_name="images",
    )
    image = models.ImageField(upload_to=product_images_directory_path, verbose_name=_("Image product"))

    class Meta:
        verbose_name = "image product"
        verbose_name_plural = "images product"


class Seller(models.Model):
    """
    Модель продавца
    name: название продавца
    description: описание продавца
    image: изображение (если есть) продавца
    phone: телефон продавца
    address: адрес продавца
    email: адрес электронной почты продавца
    created_at: когда создан продавец
    archived: статус архива продавца
    """

    class Meta:
        verbose_name = _("Seller")
        verbose_name_plural = _("Sellers")

    name = models.CharField(max_length=100, db_index=True, verbose_name=_("Name"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    image = models.ImageField(
        upload_to=seller_image_directory_path,
        null=True,
        blank=True,
        verbose_name=_("Image"),
    )
    phone = models.CharField(max_length=15, null=False, verbose_name=_("Phone"))
    address = models.TextField(null=True, blank=True, verbose_name=_("Address"))
    email = models.EmailField(max_length=100, verbose_name=_("Email"))
    products = models.ManyToManyField(
        "Product",
        blank=True,
        through="Price",
        related_name="sellers",
        verbose_name=_("Products"),
    )
    delivery_methods = ManyToManyField("Delivery", verbose_name=_("Delivery methods"))
    payment_methods = ManyToManyField("Payment", verbose_name=_("Payment methods"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    archived = models.BooleanField(default=False, verbose_name=_("Archived status"))

    class Meta:
        verbose_name = "seller"
        verbose_name_plural = "sellers"

    def __str__(self) -> str:
        return str(self.name)


class Payment(models.Model):
    """
    Модель для представления способов оплаты.

    Attributes:
        CASH (str): Константа, представляющая наличный расчет ('CH').
        CARD_ONLINE (str): Константа, представляющая оплату картой онлайн ('CO').
        CARD_COURIER (str): Константа, представляющая оплату картой курьеру ('CC').

        PAYMENT_CHOICES (tuple): Кортеж с возможными вариантами оплаты:
            - 'CH': Наличными
            - 'CO': Картой онлайн
            - 'CC': Картой курьеру
            - 'SO': Картой магазину
            - 'SR': Случайной картой магазину

        name (str): Поле для хранения выбранного способа оплаты. Доступные варианты
        определяются PAYMENT_CHOICES. По умолчанию используется наличный расчет.

    Methods:
        __str__(): Возвращает строковое представление выбранного способа оплаты.
    """

    CASH = "CH"
    CARD_ONLINE = "CO"
    CARD_COURIER = "CC"
    STORE_ONLINE = "SO"
    STORE_RANDOM = "SR"

    PAYMENT_CHOICES = (
        (CASH, _("Наличными")),
        (CARD_ONLINE, _("Картой онлайн")),
        (CARD_COURIER, _("Картой курьеру")),
        (STORE_ONLINE, _("Картой магазину")),
        (STORE_RANDOM, _("Случайной картой магазину")),
    )

    name = models.CharField(
        max_length=2,
        choices=PAYMENT_CHOICES,
        default=CASH,
        verbose_name=_("Payment method"),
        db_index=True,
        unique=True,
    )

    def __str__(self):
        return str(dict(self.PAYMENT_CHOICES).get(self.name))

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


class Delivery(models.Model):
    """
    Модель для представления способов доставки.

    Attributes:
        PICKUP_POINT (str): Константа, представляющая доставку в пункт выдачи ('PP').
        COURIER (str): Константа, представляющая курьерскую доставку ('CR').
        LOCKER (str): Константа, представляющая доставку в постамат ('LK').
        SELLER (str): Константа, представляющая доставку силами продавца ('SL').

        DELIVERY_CHOICES (list): Список с возможными вариантами доставки:
            - 'PP': В пункт выдачи
            - 'CR': Курьером
            - 'LK': В постамат
            - 'SL': Силами продавца

        name (str): Поле для хранения выбранного способа доставки. Доступные варианты
        определяются DELIVERY_CHOICES. По умолчанию используется доставка в пункт выдачи.

    Methods:
        __str__(): Возвращает строковое представление выбранного способа доставки.
    """

    PICKUP_POINT = "PP"
    COURIER = "CR"
    LOCKER = "LK"
    SELLER = "SL"
    SHOP_STANDARD = "SS"
    SHOP_EXPRESS = "SE"

    DELIVERY_CHOICES = [
        (PICKUP_POINT, _("В пункт выдачи")),
        (COURIER, _("Курьером")),
        (LOCKER, _("В постамат")),
        (SELLER, _("Силами продавца")),
        (SHOP_STANDARD, _("Магазином обычная")),
        (SHOP_EXPRESS, _("Магазином экспресс")),
    ]

    name = models.CharField(
        max_length=2,
        choices=DELIVERY_CHOICES,
        default=PICKUP_POINT,
        verbose_name=_("Delivery method"),
        db_index=True,
        unique=True,
    )

    def __str__(self):
        return str(dict(self.DELIVERY_CHOICES).get(self.name))

    class Meta:
        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")


class Price(models.Model):
    """
    Модель цены
    seller: название продавца
    product: название продукта
    quantity: доступное количество
    price: цена
    created_at: дата создания записи
    """

    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name="price",
        verbose_name=_("Seller"),
        db_index=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="prices",
        verbose_name=_("Product"),
        db_index=True,
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("Quantity"))
    sold_quantity = models.PositiveIntegerField(default=0, verbose_name=_("Sold Quantity"))
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name=_("Price"))
    created_at = models.DateField(auto_now_add=True, verbose_name=_("Created at"), null=True)

    class Meta:
        unique_together = ("product", "seller")
        verbose_name = "price"
        verbose_name_plural = "prices"

    def __str__(self):
        return f"Price(product={self.product}, seller={self.seller}), price={self.price}"


class Review(models.Model):
    """
    Модель отзыва
    product: товар к которому относится данный отзыв
    user: пользователь, который оставил отзыв
    text: текст отзыва
    created_at: время создания отзыва (создается автоматически)
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
        related_name="review",
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"))
    text = models.TextField(verbose_name=_("Text"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    update_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    updating = models.BooleanField(default=False, verbose_name=_("Updating"))

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "review"
        verbose_name_plural = "reviews"


class NameSpecification(models.Model):
    """
    Модель названия характеристики
    name: название характеристики
    """

    class Meta:
        ordering = ("name",)
        verbose_name = "name specification"
        verbose_name_plural = "names specification"

    name = models.CharField(max_length=100, db_index=True, verbose_name=_("Name specification"))

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("name",)


class Specification(models.Model):
    """
    Модель характеристики
    value: значение характеристики
    specification: название характеристики
    product: товар к которому относится данная характеристика
    """

    value = models.CharField(
        max_length=100,
        default="",
        null=False,
        blank=False,
        verbose_name=_("Value specification"),
    )
    name = models.ForeignKey(
        NameSpecification,
        on_delete=models.CASCADE,
        verbose_name=_("Name specification"),
        db_index=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("PK Product"),
        related_name="specifications",
    )

    class Meta:
        verbose_name = "specification"
        verbose_name_plural = "specifications"

    def __str__(self) -> str:
        return f"Specification(id={self.pk}, name={self.name!r}, pr)"


class Viewed(models.Model):
    """
    Модель таблицы просмотренных пользователем товаров.

    Attributes:
        user: пользователь, который посмотрел товар;
        product: товар, просмотренный пользователем;
        created_at: дата/время просмотра товара.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="viewed",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
        related_name="viewed",
    )
    created_at = models.DateTimeField(auto_now=True, verbose_name=_("Created_at"))

    class Meta:
        verbose_name = _("Viewed")
        verbose_name_plural = _("Viewed")
        ordering = ("-created_at",)
        constraints = [UniqueConstraint(fields=["user", "product"], name="user_product_unique")]

    @classmethod
    def add_viewed_product(cls, product_id: int, user: settings.AUTH_USER_MODEL) -> None:
        """
        Добавляет или обновляет товар в списке просмотренных текущим пользователем.
        Если товар просматривается текущим пользователем в первый раз,
        то увеличивается его количество просмотров.
        """

        with transaction.atomic():
            new_view, created = Viewed.objects.update_or_create(user=user, product_id=product_id)

            if created:
                product = Product.objects.select_for_update().get(id=product_id)
                product.views += 1
                product.save()

    @classmethod
    def viewed_list(cls, user: settings.AUTH_USER_MODEL, limit=20) -> QuerySet:
        """
        Возвращает список просмотренных текущим пользователем товаров (по умолчанию 20)
        """

        return (
            Viewed.objects.filter(user=user)
            .select_related("product")
            .only("product_id", "product__name")
            .order_by("-created_at")[:limit]
            .all()
        )

    @classmethod
    def viewed_count(cls, user: settings.AUTH_USER_MODEL) -> int:
        """
        Возвращает целочисленное значение количества просмотренных текущим
        пользователем товаров
        """

        return Viewed.objects.filter(user=user).count()

    @classmethod
    def exists(cls, product_id: int, user: settings.AUTH_USER_MODEL) -> bool:
        """
        Проверяет есть ли указанный товар в списке просмотренных
        текущим пользователем
        """
        return Viewed.objects.filter(user=user, product_id=product_id).exists()

    @classmethod
    def remove(cls, product_id: int, user: settings.AUTH_USER_MODEL) -> bool:
        """
        Удаляет товар из списка просмотренных текущим пользователем.
        Возвращает логическое значение результата операции.
        """
        deleted_rows, deleted_dict = Viewed.objects.filter(user=user, product_id=product_id).delete()
        return deleted_rows != 0
