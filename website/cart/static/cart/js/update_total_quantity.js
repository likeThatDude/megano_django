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
