def category_icon_directory_path(instance: "Category", filename: str) -> str:
    """Путь для сохранения иконки категории"""
    return "products/category_{name}/images/{filename}".format(
        name=instance.name,
        filename=filename,
    )


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    """Путь для сохранения изображений товаров"""
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product,
        filename=filename,
    )


def product_image_directory_path(instance: "Product", filename: str) -> str:
    """Путь для сохранения главного изображения товаров"""
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


def seller_image_directory_path(instance: "Seller", filename: str) -> str:
    """Путь для сохранения изображений продавца"""
    return "sellers/seller_{name}/images/{filename}".format(
        name=instance.name,
        filename=filename,
    )


def sort_convert(session, sort):
    """
    Конвертирует строку сортировки и обновляет параметры сортировки в сессии.

    Эта функция принимает строку сортировки и обновляет сессию с новыми параметрами сортировки.
    Если строка начинается с '-', это означает, что сортировка должна быть по возрастанию,
    иначе - по убыванию.

    Параметры:
        session (dict): Словарь сессии, в котором будут храниться параметры сортировки.
        sort (str): Строка, представляющая параметр сортировки (например, "price", "rating").

    Возвращает:
        None
    """
    temp = ""
    if "-" in sort:
        sort_param = sort[1:]
        sort = sort[1:]
        temp = "Sort-sortBy_inc"
    else:
        sort_param = f"-{sort}"
        temp = "Sort-sortBy_dec"
    session["sort_catalog"] = generate_sort_param()
    session["sort_catalog"][sort] = {
        "param": sort_param,
        "style": temp,
    }


def generate_sort_param():
    """
        Генерирует начальные параметры сортировки.

        Эта функция создает и возвращает словарь с начальными параметрами сортировки,
        которые могут быть использованы для отображения в интерфейсе. Каждый параметр
        включает в себя имя параметра и стиль сортировки.

        Возвращает:
            dict: Словарь с параметрами сортировки, где ключами являются названия
            параметров, а значениями - словари с параметрами и стилями.
    """
    return {
        "price": {
            "param": "price",
            "style": "",
        },
        "rating": {
            "param": "rating",
            "style": "",
        },
        "date": {
            "param": "date",
            "style": "",
        },
        "quantity": {
            "param": "quantity",
            "style": "",
        },
    }
