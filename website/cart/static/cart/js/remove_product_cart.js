// Функция для удаления товара в корзину
async function removeProductInCart(url, productCard) {
    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        });

        if (!response.ok) {
            throw new Error('Сеть не в порядке: ' + response.status);
        }

        // Если статус код 200, выполняем запрос на TOTAL_QUANTITY_CART
        const totalQuantityData = await getTotalQuantity(TOTAL_QUANTITY_CART);
        productCard.remove()
        await updateCartAmount(); // Обновляем общее кол-во товаров в корзине
    } catch (error) {
        console.error('Ошибка при добавлении товара в корзину:', error);
    }
}

// Добавление функций removeProductInCart всем кнопкам на странице
document.addEventListener('DOMContentLoaded', function() {
    const removeProductCards = document.querySelectorAll('.ProductCard'); // Находим все карточки товаров
    if (removeProductCards.length > 0) {
        removeProductCards.forEach(removeProductCard => { // Перебираем каждую кнопку
            const removeButton = removeProductCard.querySelector('a.btn.btn_primary')
            removeButton.addEventListener('click', async function(event) {
                event.preventDefault(); // Предотвращаем переход по ссылке href в кнопке
                const url = removeButton.getAttribute('href'); // Получаем URL из атрибута href
                await removeProductInCart(url, removeProductCard); // Вызываем функцию с переданным URL
            });
        });
    } else {
        console.warn('Кнопки удаления продукта не найдены на странице.');
    }
});
