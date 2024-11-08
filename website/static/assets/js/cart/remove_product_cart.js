// Функция для удаления товара в корзину
async function removeProductInCart(product_id, productCard) {
    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch(CART_API, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({'product_id': product_id})
        });

        if (!response.ok) {
            throw new Error('Сеть не в порядке: ' + response.status);
        }

        productCard.remove();
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
                const productId = removeButton.dataset.product_id; // Получаем URL из атрибута href
                await removeProductInCart(productId, removeProductCard); // Вызываем функцию с переданным URL
                await updateTotalValuesCart(); // Обновляем общее кол-во товаров
            });
        });
    } else {
        console.warn('Кнопки удаления продукта не найдены на странице.');
    }
});
