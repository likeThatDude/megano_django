function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



async function addProductInCart(url) {
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
        await updateCartAmount(); // Обновляем общее кол-во товаров в корзине
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
