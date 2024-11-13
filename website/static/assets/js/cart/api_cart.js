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

// Функция выполняет GET запрос на API (возвращает информацию о корзине)
async function getAPICart() {
    try {
        const response = await fetch(CART_API);
        const responseData = response.json();
        return responseData;
    } catch (error) {
        console.error('Ошибка при выполнении GET запроса:', error);
        throw error;
    }
}

// Функция выполняет POST запрос на API (добавляет товар в корзину)
async function postAPICart(data) {
    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch(CART_API, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error('Ошибка добавления товара в корзину ' + response.status);
        }
    } catch (error) {
        console.error('Ошибка при выполнении POST запроса:', error);
    }
}

// Функция выполняет PATCH запрос на API (обновляет товар в корзине)
async function patchAPICart(data) {
    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch(CART_API, {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error('Ошибка обновления товара в корзине ' + response.status);
        }
    } catch (error) {
        console.error('Ошибка при выполнении PATCH запроса:', error);
    }
}

// Функция выполняет DELETE запрос на API (удаляет товар в корзине)
async function deleteAPICart(data) {
    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch(CART_API, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error('Ошибка удаления товара в корзине ' + response.status);
        }
    } catch (error) {
        console.error('Ошибка при выполнении DELETE запроса:', error);
    }
}
