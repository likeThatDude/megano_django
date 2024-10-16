from catalog.models import Category, ProductImage


def category_icon_directory_path(instance: Category, filename: str) -> str:
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
