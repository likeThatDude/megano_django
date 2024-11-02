async function getTotalPrice() {
    try {
        const response = await fetch(TOTAL_PRICE_CART);

        if (!response.ok) {
            throw new Error('Сеть не в порядке: ' + response.status);
        }

        const data = await response.json();
        const totalPrice = data.total_price;
        return totalPrice
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        throw error;
    }
}

// Функция для получения общего кол-ва товаров в корзине
async function getTotalQuantity() {
    try {
        const response = await fetch(TOTAL_QUANTITY_CART);

        if (!response.ok) {
            throw new Error('Сеть не в порядке: ' + response.status);
        }

        const data = await response.json();
        const totalQuantity = data.total_quantity;
        return totalQuantity; // Возвращаем полученные данные
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        throw error; // Пробрасываем ошибку дальше, если нужно
    }
}


// Функция для обновления элемента CartBlock-amount
async function updateCartAmount() {
    const totalQuantity = await getTotalQuantity(TOTAL_QUANTITY_CART); // Получаем общее количество
    const totalPrice = await getTotalPrice(TOTAL_PRICE_CART); // Получаем общую стоимость
     // Получаем элемент для отображения кол-ва товаров в корзине
    const cartAmountElement = document.querySelector('.CartBlock-amount');
     // Получаем элемент для отображения общей стоимости товаров в корзине
    const cartBlockPrice = document.querySelector('.CartBlock-price');

    if (cartAmountElement) { // Проверяем, существует ли элемент
        cartAmountElement.innerText = totalQuantity; // Обновляем текст элемента
        cartBlockPrice.innerText = totalPrice
    } else {
        console.warn('Элемент с классом "CartBlock-amount" не найден.');
    }
}

// Выполняем обновление при полной загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    updateCartAmount(); // Вызываем функцию для обновления количества в корзине
});
