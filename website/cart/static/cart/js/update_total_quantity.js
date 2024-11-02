// Функция для получения общего кол-ва товаров в корзине
async function getTotalQuantity() {
    try {
        const response = await fetch(TOTAL_QUANTITY_CART);

        if (!response.ok) {
            throw new Error('Сеть не в порядке: ' + response.status);
        }

        const data = await response.json(); // Предполагаем, что ответ в формате JSON
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
    const cartAmountElement = document.querySelector('.CartBlock-amount'); // Получаем первый элемент по классу

    if (cartAmountElement) { // Проверяем, существует ли элемент
        cartAmountElement.innerText = totalQuantity; // Обновляем текст элемента
    } else {
        console.warn('Элемент с классом "CartBlock-amount" не найден.');
    }
}

// Выполняем обновление при полной загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    updateCartAmount(); // Вызываем функцию для обновления количества в корзине
});
