// Функция для добавления товара в корзину
async function addProductInCart(data) {
    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch(CART_API, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Сеть не в порядке: ' + response.status);
        }

        // Если статус код 200, выполняем запрос на TOTAL_QUANTITY_CART

        await updateTotalValuesCart(); // Обновляем общее кол-во товаров в корзине
    } catch (error) {
        console.error('Ошибка при добавлении товара в корзину:', error);
    }
}


// Собираем информацию из элемента
async function getInfoProduct(elem) {
    const data_elem = []
    data_elem.push({
        product_id: elem.dataset.product_id,
        price_id: elem.dataset.price_id,
    })
    return data_elem
}

// Добавление функций addProductInCart всем кнопкам на странице
document.addEventListener('DOMContentLoaded', function() {
    const cartButtons = document.querySelectorAll('.Card-btn'); // Находим все кнопки с классом Card-btn
    if (cartButtons.length > 0) { // Проверяем, существуют ли кнопки
        cartButtons.forEach(cartButton => { // Перебираем каждую кнопку
            cartButton.addEventListener('click', async function(event) {
                event.preventDefault(); // Предотвращаем переход по ссылке href в кнопке
                const data_cart_btn = await getInfoProduct(cartButton); // Собираем product_id, price_id с кнопки
                await addProductInCart(data_cart_btn); // Вызываем функцию с переданным URL
            });
        });
    } else {
        console.warn('Кнопки корзины не найдены на странице.');
    }
});
