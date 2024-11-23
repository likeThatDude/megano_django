// Функция для обновления статуса
let hideTimeoutId;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Проверяем, начинается ли cookie с нужного имени
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateStatus(title, text, statusClass, buttonClass) {
    // Получаем блок статуса
    const statusArea = document.querySelector('.operation_status_area');

    // Проверяем, виден ли уже блок
    if (statusArea.classList.contains('show')) {
        // Если блок виден, скрываем его перед обновлением
        statusArea.classList.remove('show');
        statusArea.classList.add('hide');

        // Ждем окончания анимации, а затем показываем блок с новыми данными
        setTimeout(() => {
            // Обновляем текстовые данные
            document.querySelector('.status_header p').textContent = title;
            document.querySelector('.message_status_block p').textContent = text;

            // Меняем статусный класс
            statusArea.classList.remove('green_status', 'red_status', 'yellow_status');
            statusArea.classList.add(statusClass);

            const deleteButton = document.querySelector('.delete_button_status');
            deleteButton.classList.remove('delete_button_status_green', 'delete_button_status_red');
            deleteButton.classList.add(buttonClass);

            // Показываем блок с новыми данными
            statusArea.classList.remove('hide');
            statusArea.classList.add('show');
        }, 500); // Задержка в 500 мс, чтобы успела анимация скрытия
    } else {
        // Если блок не виден, сразу обновляем и показываем
        document.querySelector('.status_header p').textContent = title;
        document.querySelector('.message_status_block p').textContent = text;

        statusArea.classList.remove('green_status', 'red_status', 'yellow_status');
        statusArea.classList.add(statusClass);

        const deleteButton = document.querySelector('.delete_button_status');
        deleteButton.classList.remove('delete_button_status_green', 'delete_button_status_red');
        deleteButton.classList.add(buttonClass);

        // Показываем блок с новыми данными
        statusArea.classList.remove('hide');
        statusArea.classList.add('show');
    }

    // Если существует предыдущий таймер, то отменяем его
    if (hideTimeoutId) {
        clearTimeout(hideTimeoutId);
    }

    // Устанавливаем новый таймер, чтобы скрыть блок через 5 секунд
    hideTimeoutId = setTimeout(() => {
        statusArea.classList.remove('show');
        statusArea.classList.add('hide');
    }, 5000);
}

document.querySelector('.delete_button_status').addEventListener('click', function () {
    // Получаем родительский элемент .operation_status_area
    const statusArea = document.querySelector('.operation_status_area');

    // Убираем класс 'show' и добавляем 'hide', чтобы скрыть блок
    statusArea.classList.remove('show');
    statusArea.classList.add('hide');
});


// Основной обработчик клика по кнопке
document.querySelectorAll('.Card-btn-comp').forEach(function (button) {
    button.addEventListener('click', function (e) {
        e.preventDefault(); // Предотвращаем стандартное поведение кнопки (перезагрузку страницы)

        // Получаем csrf токен
        const csrfToken = getCookie('csrftoken');

        // Получаем product_id из родительской формы, в которой находится кнопка
        const productId = button.closest('form').querySelector('input[name="product_id"]').value;

        // Формируем запрос
        fetch(COMPARISON_ADD_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Передаем CSRF токен
            },
            body: JSON.stringify({product_id: productId}) // Отправляем product_id
        })
            .then(response => response.json())
            .then(data => {
                // В случае успеха
                if (data.status === null) {
                    // Обрабатываем случай, если status равен null
                    updateStatus(data.title, data.text, 'yellow_status', 'delete_button_status_green');
                } else if (data.status === false) {
                    // Обрабатываем случай, если status равен false
                    updateStatus(data.title, data.text, 'red_status', 'delete_button_status_red');
                } else if (data.status) {
                    // В случае успешного ответа (status true)
                    updateStatus(data.title, data.text, 'green_status', 'delete_button_status_green');
                }

            })
            .catch(error => {
                console.error('Ошибка:', error);
                // В случае ошибки запроса
                updateStatus('Ошибка', 'Произошла ошибка при добавлении товара.'); // Обновляем статус для ошибки
                alert("Произошла ошибка при добавлении товара.");
            });
    });
});

document.querySelectorAll('.DeleteLink').forEach(function (button) {
    button.addEventListener('click', function (e) {
        e.preventDefault(); // Предотвращаем стандартное поведение кнопки (отправку формы)

        // Находим родительскую форму и извлекаем значение product_id
        const form = button.closest('form');
        const productId = form.querySelector('input[name="product_id"]').value;


        // Получаем CSRF-токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;


        // Отправляем DELETE-запрос на сервер
        fetch(DELETE_PRODUCT, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Передаем CSRF-токен
            },
            body: JSON.stringify({product_id: productId}) // Отправляем product_id
        })
            .then(response => response.json())
            .then(data => {
                // В случае успеха
                if (data.status === null) {
                    // Обрабатываем случай, если status равен null
                    updateStatus(data.title, data.text, 'yellow_status', 'delete_button_status_green');
                } else if (data.status === false) {
                    // Обрабатываем случай, если status равен false
                    updateStatus(data.title, data.text, 'red_status', 'delete_button_status_red');
                } else if (data.status) {
                    // В случае успешного ответа (status true)
                    updateStatus(data.title, data.text, 'green_status', 'delete_button_status_green');
                    const productCard = button.closest('.ProductCard-desc');
                    if (productCard) {
                        productCard.remove();  // Удаляем весь блок карточки
                    }
                }

            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
    });
});
