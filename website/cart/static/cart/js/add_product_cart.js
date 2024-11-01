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

async function addProductInCart(url) {
    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error('Сеть не в порядке: ' + response.status);
        }

        // Если статус код 200, выполняем запрос на TOTAL_QUANTITY_CART
        const totalQuantityData = await getTotalQuantity(TOTAL_QUANTITY_CART);

        // Обновляем элемент на странице
        const cartAmountElement = document.querySelector('.CartBlock-amount');
        if (cartAmountElement) {
            cartAmountElement.innerText = totalQuantityData; // Убедитесь, что вы обращаетесь к правильному ключу
        } else {
            console.warn('Элемент с классом "CartBlock-amount" не найден.');
            }
    } catch (error) {
        console.error('Ошибка при добавлении товара в корзину:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const cartButtons = document.querySelectorAll('.Card-btn'); // Находим все кнопки с классом Card-btn
    if (cartButtons.length > 0) { // Проверяем, существуют ли кнопки
        cartButtons.forEach(cartButton => { // Перебираем каждую кнопку
            cartButton.addEventListener('click', async function(event) {
                event.preventDefault(); // Предотвращаем переход по ссылке href в кнопке
                const url = cartButton.getAttribute('href'); // Получаем URL из атрибута href
                await addProductInCart(url); // Вызываем функцию с переданным URL
            });
        });
    } else {
        console.warn('Кнопки корзины не найдены на странице.');
    }
});
