// Функция для получения куков по имени
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

// Функция для получения общей стоимости корзины
async function getTotalValues() {
    try {
        const response = await fetch(CART_API);

        if (!response.ok) {
            throw new Error('Сеть не в порядке: ' + response.status);
        }

        const data = await response.json();
        const total_values = {
            'total_cost': data.cart.total_cost,
            'total_quantity': data.cart.total_quantity,
        }
        return total_values
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        throw error;
    }
}


// Функция для обновления элемента CartBlock-amount
async function updateTotalValuesCart() {
    const totalValues = await getTotalValues(); // Получаем общие значения корзины (кол-во товаров, стоимость)
     // Получаем элемент для отображения кол-ва товаров в корзине
    const cartAmountElement = document.querySelector('.CartBlock-amount');
     // Получаем элемент для отображения общей стоимости товаров в корзине
    const cartBlockPrice = document.querySelector('.CartBlock-price');

    if (cartAmountElement) { // Проверяем, существует ли элемент
        cartAmountElement.innerText = totalValues.total_quantity; // Обновляем кол-во товаров к корзине
        cartBlockPrice.innerText = totalValues.total_cost; // Обновляем стоимость товаров в корзине
    } else {
        console.warn('Элемент с классом "CartBlock-amount" не найден.');
    }
}

// Выполняем обновление при полной загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    updateTotalValuesCart(); // Вызываем функцию для обновления количества в корзине
});
