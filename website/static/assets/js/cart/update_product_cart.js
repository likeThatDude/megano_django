// Функция для сбора данных со страницы для отправки
async function getInfoToUpdateCart() {
    const allInputs = document.querySelectorAll('input.Amount-input');
    const allSelects = document.querySelectorAll('select.Select-seller-product');
    const data = {};
    allInputs.forEach(input => {
        const product_id = input.dataset.product_id;
        const quantity = input.value;

        const select = Array.from(allSelects).find(select => select.dataset.product_id === product_id);
        const seller_id = select ? select.value : null; // Получаем value выбранного option, если select найден

        data[product_id] = {
            'product_id': product_id,
            'quantity': Number(quantity),
            'seller_id': Number(seller_id),
        }
    });
    return data
}

// Функция для обновления кол-ва товаров в корзине
async function updateProductInCart() {
    try {
        const csrftoken = getCookie('csrftoken');

        const dataToReq = await getInfoToUpdateCart()
        const response = await fetch(CART_API, {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dataToReq)
        });

        await updateTotalValuesCart();

        if (!response.ok) {
            throw new Error('Сеть не в порядке: ' + response.status);
        }
    } catch (error) {
        console.error('Ошибка при обновлении товаров в корзине:', error);
    }
}

// Добавление функции updateProductInCart кнопке 'перейти к оформлению'
document.addEventListener('DOMContentLoaded', function() {
    const btnPlaceOrder = document.querySelector('.btn_place_an_order');
    btnPlaceOrder.addEventListener('click', async function(event) {
        event.preventDefault(); // Предотвращаем переход по ссылке href в кнопке
        await updateProductInCart();
        await updateTotalValuesCart(); // Обновляем общее кол-во товаров
    })
})
