// Функция для сбора информации о товаре в карточке товаров
async function getDataProductInCart(productCard) {
    const productId = productCard.dataset.product_id;
    const quantityProduct = Number(productCard.querySelector('.Amount-input').value);
    const sellerProductId = productCard.querySelector('.Select-seller-product').value;
    const data = {
    "product_id": productId,
    "quantity": quantityProduct,
    "seller_id": sellerProductId,
    };
    return data
}

// Функция для сбора информации для добавления товара в корзину
async function getDataFromButton(addButton) {
    const productId = addButton.dataset.product_id;
    const priceId = addButton.dataset.price_id;
    const data = {
        "product_id": productId,
        "price_id": priceId,
    };
    return data
}
