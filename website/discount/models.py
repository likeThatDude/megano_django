from decimal import Decimal
from random import choices
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from catalog.models import Category
from catalog.models import Price
from catalog.models import Product
from django.db import models
from django.db.models import Max
from django.db.models import Min
from django.db.models import Q
from django.db.models import QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pytils.translit import slugify


class ProductGroup(models.Model):
    """
    Модель группы товаров. Используется как вспомогательная таблица для
    реализации вида скидки "Скидка на наборы(группы)".

    Attributes:
        name: название группы
        description: описание группы
        products: связь многие-ко-многим с товарами, которые относятся к данной группе
    """

    name = models.CharField(unique=True, max_length=100, verbose_name=_("Name"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    archived = models.BooleanField(default=False, verbose_name=_("Archived status"))

    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="product_groups",
        verbose_name=_("Products"),
        db_table="discount_groups_products",
    )

    class Meta:
        verbose_name = _("Product group")
        verbose_name_plural = _("Product groups")
        ordering = ("name",)
        db_table = "discount_group"

    def __str__(self) -> str:
        return f"{self.pk}. {self.name}"


class Discount(models.Model):
    """
    Модель скидки

    Attributes:
        name: название скидки
        kind: вид скидки. Скидка может быть следующих видов:
            - Скидка на товар: скидка на список товаров и/или на категории товаров;
            - Скидка на наборы: применяется, если товары из корзины состоят в указанных группах;
            - Скидка на корзину: применяется, если общая стоимость товаров в корзине выше total_cost_l и
                при этом количество товаров в диапазоне от quantity_l до quantity_g
        priority: приоритет скидки. Если на товар действует несколько скидок, то применяется
            самая тяжёлая (приоритетная) скидка
        method: механизм скидки. Скидка может иметь следующие механизмы расчета:
            - Процент скидки;
            - Сумма скидки - сумма вычета из стоимости товара;
            - Фиксированная стоимость для каждого товара
        quantity_l: наименьшее количество товаров в корзине. Поле используется только при выборе
            скидки на корзину
        quantity_g: наибольшее количество товаров в корзине. Поле используется только при выборе
            скидки на корзину
        total_cost_l: значение общей стоимости товаров в корзине, при превышении которой будет
            действовать скидка на корзину
        percent: процент применяемой скидки, если выбран механизм скидки "Процент скидки"
        price: значение суммы скидки в используемой валюте, если выбран механизм скидки "Сумма скидки". Итоговая стоимость
            товаров, если выбран "Фиксированная итоговая стоимость"
        description: описание скидки
        start_date: дата начала действия скидки
        end_date: дата окончания действия скидки
        is_active: статус актуальности скидки
        archived: механизм мягкого удаления скидки
        products: связь многие-ко-многим с продуктами, к которым применима скидка. Связь используется,
            если выбран вид скидки "Скидка на товар"
        categories: связь многие-ко-многим с категориями товаров, к которым применима скидка. Связь
            используется, если выбран вид скидки "Скидка на товар"
        product_groups: связь многие-ко-многим с группами товаров, к которым применима скидка. Связь
            используется, если выбран вид скидки "Скидка на наборы"
    """

    # виды скидок
    PRODUCT = "PT"
    SET = "ST"
    CART = "CT"

    KIND_CHOICES = [
        (PRODUCT, _("Product discount")),
        (SET, _("Discount on kits")),
        (CART, _("Discount on cart")),
    ]

    # типы механизмов расчёта скидки
    PERCENT = "PT"
    SUMM = "SM"
    FIXED = "FD"

    METHOD_CHOICES = [
        (PERCENT, _("Discount percentage")),
        (SUMM, _("Discount amount")),
        (FIXED, _("Fixed cost")),
    ]

    # приоритеты скидок
    THE_LOWEST = 1
    LOW = 2
    MIDDLE = 3
    HIGH = 4
    THE_HIGHEST = 5

    PRIORITY_CHOICES = [
        (THE_LOWEST, _("Lowest")),
        (LOW, _("Low")),
        (MIDDLE, _("Middle")),
        (HIGH, _("High")),
        (THE_HIGHEST, _("Highest")),
    ]

    name = models.CharField(unique=True, max_length=100, verbose_name=_("Name"))
    kind = models.CharField(max_length=2, choices=KIND_CHOICES, verbose_name=_("Type of discount"))
    method = models.CharField(max_length=2, choices=METHOD_CHOICES, verbose_name=_("Discount mechanism"))
    priority = models.PositiveSmallIntegerField(
        default=MIDDLE,
        choices=PRIORITY_CHOICES,
        verbose_name=_("Discount priority"),
        help_text=_(
            "If there are several discounts on the product, then the heaviest (priority) discount is applied. "
        ),
    )
    quantity_l = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("The least amount"),
        help_text=_("Set the lower limit of the quantity of goods/s if the 'Discount on cart' type is selected. "),
    )
    quantity_g = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("The largest number"),
        help_text=_("Set the upper limit of the quantity of goods/s if the 'Discount on cart' type is selected. "),
    )
    total_cost_l = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Total cost"),
        help_text=_(
            "Enter the value of the total cost of the items in the cart, "
            "if exceeded, the discount on the basket will apply. "
        ),
    )
    percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("Discount percentage"),
        help_text=_("Enter the discount percentage if the 'Discount Percentage' mechanism is used. "),
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("The discount value in the currency used"),
        help_text=_(
            "Enter the discount value in the currency used if the 'Discount Amount' or 'Fixed Cost' mechanism is used."
        ),
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name="Slug",
        help_text=_("It is automatically generated on behalf of, but can be changed"),
    )
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    start_date = models.DateField(default=timezone.now, verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active?"))
    archived = models.BooleanField(default=False, verbose_name=_("Archived status"))

    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="discounts",
        verbose_name=_("Products"),
        db_table="discounts_products",
        help_text=_("Add products if the 'Product Discount' type is selected. "),
    )
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="discounts",
        verbose_name=_("Categories"),
        db_table="discounts_categories",
        help_text=_("Add categories if the 'Product Discount' type is selected. "),
    )
    product_groups = models.ManyToManyField(
        ProductGroup,
        blank=True,
        related_name="discounts",
        verbose_name=_("Product groups"),
        db_table="discounts_groups",
        help_text=_("Add groups if the 'Discount on Sets' view is selected. "),
    )

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")
        ordering = (
            "-priority",
            "-start_date",
        )
        db_table = "discount"

    def __str__(self) -> str:
        return f"{self.pk}. {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug or self.name != Discount.objects.filter(pk=self.pk).first().name:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("discount:discount-detail", kwargs={"slug": self.slug})

    @classmethod
    def __get_discounts_queryset(cls, products: Sequence[Product] | Product) -> QuerySet:
        """
        Возвращает QuerySet c уникальными объектами скидок, для указанных товаров/товара.
        Используется во избежание дублирования кода в методах cls.get_discounts и cls.get_priority_discount
        """

        today = timezone.now().date()

        if isinstance(products, Product):
            products = [products]

        return (
            Discount.objects.filter(
                Q(
                    products__in=products,
                    categories__products__in=products,
                    is_active=True,
                    archived=False,
                    start_date__lte=today,
                    end_date__gte=today,
                )
                | Q(
                    products__in=products,
                    is_active=True,
                    archived=False,
                    start_date__lte=today,
                    end_date__gte=today,
                )
                | Q(
                    categories__products__in=products,
                    is_active=True,
                    archived=False,
                    start_date__lte=today,
                    end_date__gte=today,
                )
            )
            .distinct()
            .order_by(
                "-priority",
                "-start_date",
            )
            .defer(
                "name",
                "priority",
                "description",
                "start_date",
                "end_date",
                "is_active",
                "archived",
                "quantity_l",
                "quantity_g",
                "total_cost_l",
            )
        )

    @classmethod
    def get_discounts(cls, products: Sequence[Product] | Product) -> QuerySet:
        """
        Возвращает все скидки на указанный список товаров или на один товар.
        Вид возвращаемых скидок "Скидка на товар", точнее - скидка на
        список товаров или/и категории товаров.

        Attributes:
            products: товар или список товаров

        Returns:
            Sequence[Discount]: список скидок
        """

        return cls.__get_discounts_queryset(products).all()

    @classmethod
    def get_priority_discount(cls, products: Sequence[Product] | Product) -> Optional["Discount"]:
        """
        Возвращает приоритетную скидку на указанный список товаров или на один товар.
        Вид возвращаемой скидки "Скидка на товар", точнее - скидка на
        список товаров или/и категории товаров.

        Если передать список товаров, то функция ищет скидку, которая действует на все товары из списка.
        Возвращает приоритетную скидку, или None.

        Если для списка не нашлось подходящей скидки, используйте этот в метод в цикле для каждого
        из товара в списке. Иначе говоря, если нет скидки на список товаров, то можно найти скидки,
        которые действуют отдельно для каждого товара из списка.

        Attributes:
            products: товар или список товаров

        Returns:
            Discount: приоритетная скидка или None
        """

        if isinstance(products, Product):
            return cls.__get_discounts_queryset(products).first()

        priority_discount: Discount = cls.__get_discounts_queryset(products).first()

        if priority_discount:
            discounted_products = priority_discount.products.all()
            discounted_categories = Category.objects.filter(
                id__in=priority_discount.categories.values_list("id", flat=True)
            )
            products_from_discounted_categories = Product.objects.filter(category__in=discounted_categories)
            products_from_priority_discount = set(discounted_products.union(products_from_discounted_categories))

            if set(products).issubset(products_from_priority_discount):
                return priority_discount

    @classmethod
    def get_discounted_price(
        cls, product: Product, discount: "Discount", price: Decimal = None
    ) -> Dict[str, Product | Decimal | bool]:
        """
        Рассчитывает цену продукта с учётом скидки в зависимости от механизма скидки.

        Attributes:
            product (Product): продукт из корзины
            discount (Discount): скидка, которая действует на продукт
            price (Decimal): исходная цена продукта. Если цена не передана, то скидка рассчитывается
                на основе максимальной цены на данный продукт
        Returns:
            Dict: возвращает словарь, например
                {'product': Product, 'price': Decimal, 'discounted_price': Decimal, is_discounted: bool}
        """

        if price is None:
            price = Price.objects.filter(product=product).aggregate(Max("price"))["price__max"] or 0

        cart_elem = {
            "product": product,
            "price": price,
            "is_discounted": True,
        }
        if discount is None:
            cart_elem.update(discounted_price=price, is_discounted=False)
            return cart_elem

        if discount.method == Discount.PERCENT:
            cart_elem.update(discounted_price=price - (price * discount.percent / 100))
            return cart_elem

        if discount.method == Discount.SUMM:
            discounted_price = price - discount.price
            cart_elem.update(discounted_price=discounted_price if discounted_price > 0 else 1)
            return cart_elem

        if discount.method == Discount.FIXED:
            cart_elem.update(discounted_price=discount.price)
            return cart_elem

    @classmethod
    def get_cart_discount(cls, cart: List[Dict[str, Product | Decimal]]) -> List[Dict[str, Product | Decimal | bool]]:
        """
        Метод ищет приоритетную скидку на корзину или набор/группу на основе коллекции позиций корзины.
        Если такая скидка не найдена, то ищет приоритетную скидку на список товаров из корзины.
        Если и такая скидка не найдена, то ищет приоритетную скидку для каждого товара по отдельности.

        Attributes:
            cart: коллекция позиций корзины вида {'product': Product, 'price': Decimal}

        Returns:
            List[Dict]: возвращает коллекцию словарей, например
                [{'product': Product, 'price': Decimal, 'discounted_price': Decimal, is_discounted: bool}, ...]
        """

        today = timezone.now().date()
        products = [elem["product"] for elem in cart]

        cart_priority_discount: Discount = (
            Discount.objects.filter(
                Q(
                    quantity_l__lte=len(cart),
                    quantity_g__gte=len(cart),
                    total_cost_l__lte=sum([elem["price"] for elem in cart if elem["price"]]),
                    is_active=True,
                    archived=False,
                    start_date__lte=today,
                    end_date__gte=today,
                )
                | Q(
                    product_groups__products__in=products,
                    is_active=True,
                    archived=False,
                    start_date__lte=today,
                    end_date__gte=today,
                )
            )
            .order_by(
                "-priority",
                "-start_date",
            )
            .defer("name", "priority", "description", "start_date", "end_date", "is_active", "archived")
            .first()
        )

        if cart_priority_discount:
            # расчёт скидки если применяется скидка на корзину
            if cart_priority_discount.kind == Discount.CART:
                return [
                    cls.get_discounted_price(elem["product"], cart_priority_discount, elem["price"]) for elem in cart
                ]

            # проверка на наличие всех указанных продуктов в группах, на которые действует скидка
            if cart_priority_discount.kind == Discount.SET:
                products_from_discounted_groups = Product.objects.filter(
                    product_groups__in=cart_priority_discount.product_groups.all()
                ).all()

                # расчёт скидки если применяется скидка на наборы/группу
                if set(products).issubset(set(products_from_discounted_groups)):
                    return [
                        cls.get_discounted_price(elem["product"], cart_priority_discount, elem["price"])
                        for elem in cart
                    ]

        products_priority_discount = cls.get_priority_discount(products)
        # расчёт скидки, если применяется скидка на список товаров и/или категории
        if products_priority_discount:
            return [
                cls.get_discounted_price(elem["product"], products_priority_discount, elem["price"]) for elem in cart
            ]

        # поиск скидки на каждый товар и расчёт цены со скидкой
        return [
            cls.get_discounted_price(elem["product"], cls.get_priority_discount(elem["product"]), elem["price"])
            for elem in cart
        ]

    @classmethod
    def get_discounted_products(cls, amount: int) -> List[Product]:
        """
        Возвращает список случайных товаров,
        на которые действует какая-нибудь скидка
        :param amount: количество случайных товаров в списке
        """

        today = timezone.now().date()
        discounted_products = (
            Product.objects.filter(
                Q(
                    discounts__is_active=True,
                    discounts__archived=False,
                    discounts__isnull=False,
                    discounts__start_date__lte=today,
                    discounts__end_date__gte=today,
                    category__discounts__is_active=True,
                    category__discounts__archived=False,
                    category__discounts__isnull=False,
                    category__discounts__start_date__lte=today,
                    category__discounts__end_date__gte=today,
                )
                | Q(
                    discounts__is_active=True,
                    discounts__archived=False,
                    discounts__isnull=False,
                    discounts__start_date__lte=today,
                    discounts__end_date__gte=today,
                )
                | Q(
                    category__discounts__is_active=True,
                    category__discounts__archived=False,
                    category__discounts__isnull=False,
                    category__discounts__start_date__lte=today,
                    category__discounts__end_date__gte=today,
                )
                | Q(
                    product_groups__discounts__is_active=True,
                    product_groups__discounts__archived=False,
                    product_groups__discounts__isnull=False,
                    product_groups__discounts__start_date__lte=today,
                    product_groups__discounts__end_date__gte=today,
                )
            )
            .annotate(
                price=Min("prices__price"),
            )
            .all()
        )
        try:
            return choices(discounted_products, k=amount)
        except IndexError:
            return []
