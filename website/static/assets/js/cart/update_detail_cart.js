// Функция получения динамического кол-ва товаров в корзине
async function getDynamicTotalQuantity() {
    const allInputs = document.querySelectorAll('.Amount-input');
    let total = 0;

    allInputs.forEach(input => {
        const value = parseFloat(input.value) || 0;
        total += value;
    });
    return total;
}


// Функция обновляет кол-ва товара в футере корзине (возле кнопки "перейти к оформлению")
async function footerUpdateQuantityCart(newQuantity) {
    const footerQuantity = document.querySelector('.Footer-quantity-products-cart');
    footerQuantity.innerText = newQuantity;
}

// Функция обновляет стоимость товара на странице корзины (используется jQuery)
async function updateCostProduct(productCard) {
    var thisCostProduct = productCard.querySelector('.Cost-product-value');
    var quantityProduct = productCard.querySelector('.Amount-input').value;
    var priceProduct = parseFloat(productCard.dataset.price_product);
    var newCostProduct = parseFloat(quantityProduct * priceProduct);
    thisCostProduct.innerText = String(newCostProduct.toFixed(2)) + ' $';
}

// Добавление функционала обновления товаров кнопке "перейти к оформлению"
const buttonPlaceOrder = document.querySelector('.btn_place_an_order')
buttonPlaceOrder.addEventListener('click', async function(event) {
    event.preventDefault();
    const productCards = document.querySelectorAll('.ProductCard');
    for (const productCard of productCards) {
    const data = await getDataProductInCart(productCard); // Получаем инфу со страницы
    await patchAPICart(data);  // Обновляем эту инфу в корзине на беке
    updateTotalQuanCost(); // Обновляем инфу в хедере
    }
})

async function changePriceProduct(productCard, newPriceProduct) {
    productCard.dataset.price_product = newPriceProduct;
}

// Функция обновления всей карточки товаров (используется в select`е выбора продавца)
async function selectUpdateProductCard(selectElement) {
    const productCard = selectElement.closest('.ProductCard');
    const dataProduct = await getDataProductInCart(productCard);
    await patchAPICart(dataProduct);

    const newData = await getAPICart();
    const productId = Number(productCard.dataset.product_id);
    const newPriceProduct = newData.products[productId].price;
    const newTotalQuantity = newData.total_quantity;

    await changePriceProduct(productCard, newPriceProduct);
    await updateCostProduct(productCard);
    await updateTotalQuanCost();
    await footerUpdateQuantityCart(newTotalQuantity);
}
