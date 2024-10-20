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