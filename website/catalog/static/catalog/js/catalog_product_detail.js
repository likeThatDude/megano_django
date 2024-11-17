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

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('reviewForm');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const reviewText = document.getElementById('review').value;
        const noReviewBlock = document.getElementById('no_review');
        const csrftoken = getCookie('csrftoken');

        const data = {
            text: reviewText,
            product: product_id,
        };

        try {
            const response = await fetch(CREATE_REVIEW, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                if (noReviewBlock) {
                    noReviewBlock.style.display = 'none';
                }
                const reviewData = await response.json();

                const reviewsContainer = document.getElementById('reviews');
                const reviewHeader = reviewsContainer.querySelector('.Section-header');

                if (reviewsContainer && reviewHeader) {
                    const reviewElement = createReviewElement(reviewData);
                    reviewHeader.insertAdjacentHTML('afterend', reviewElement);
                }

                const countElement = document.querySelector('.Section-title');
                if (countElement) {
                    const currentCount = parseInt(countElement.textContent.match(/\d+/)[0]);
                    countElement.innerHTML = `Отзывов: ${currentCount + 1} шт.`;

                }

                const secondCountElement = document.getElementById('main-count');
                if (secondCountElement) {
                    const currentCount = parseInt(secondCountElement.textContent.match(/\d+/)[0]);
                    secondCountElement.innerHTML = `Отзывы ${currentCount + 1}`;
                }

                form.reset();
            } else {
                const errorData = await response.json();
            }
        } catch (error) {
            console.error('Ошибка при отправке отзыва:', error);
        }
    });
});

function createReviewElement(review) {
    const createdAt = new Date(review.created_at);

    const monthOptions = {month: 'long'}; // Полное название месяца
    const month = createdAt.toLocaleDateString('ru-RU', monthOptions).toUpperCase();
    const day = createdAt.getDate(); // Число месяца
    let reviewId = review.pk
    const deleteUrl = deleteReviewUrl.replace("0", reviewId);
    const updateUrl = updateReviewUrl.replace("0", reviewId);

    return `
        <div class="Comments">
            <div class="Comment">
                <div class="Comment-column Comment-column_pict">
                    <div class="Comment-avatar">
                    </div>
                </div>
                <div class="Comment-column">
                    <header class="Comment-header">
                        <div>
                            <strong class="Comment-title">${current_user}</strong>
                            <span class="Comment-date">
                                ${month} ${day}&nbsp;/&nbsp;
                                ${createdAt.getFullYear()}&nbsp;/&nbsp;
                                ${createdAt.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'})}
                            </span>
                        </div>
                    </header>
                    <div class="Comment-content">
                        ${review.text}
                    </div>
                </div>
                <div class="User-control">
                    <button class="UpdateDeleteReviewButton" 
                            data-review-id="${review.pk}"
                            data-update-url="${updateUrl}">
                        редактировать
                    </button>
                    <button class="UpdateDeleteReviewButton" 
                            data-review-id="${review.pk}"
                            data-delete-url="${deleteUrl}">
                        удалить
                    </button>
                </div>
            </div>
        </div>
    `;
}


document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', async (event) => {
        if (event.target.classList.contains('UpdateDeleteReviewButton') && event.target.hasAttribute('data-review-id')) {
            const button = event.target;
            const deleteUrl = button.getAttribute('data-delete-url');
            const csrftoken = getCookie('csrftoken');
            const noReviewBlock = document.getElementById('no_review');
            const secondCountElement = document.getElementById('main-count');
            const currentCount = parseInt(secondCountElement.textContent.match(/\d+/)[0]);

            try {
                const response = await fetch(deleteUrl, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': csrftoken,
                    },
                });

                if (response.ok) {
                    const commentBlock = button.closest('.Comment');
                    commentBlock.remove();
                    const countElement = document.querySelector('.Section-title');
                    if (countElement) {
                        const currentCount = parseInt(countElement.textContent.match(/\d+/)[0]);
                        countElement.innerHTML = `Отзывов: ${currentCount - 1} шт.`;
                    }
                    const secondCountElement = document.getElementById('main-count');
                    if (secondCountElement) {
                        const currentCount = parseInt(secondCountElement.textContent.match(/\d+/)[0]);
                        secondCountElement.innerHTML = `Отзывы ${currentCount - 1}`;
                    }
                    if (currentCount === 1) {
                        noReviewBlock.style.display = 'block';
                    }
                } else {
                    const errorData = await response.json();
                }
            } catch (error) {
                console.error('Ошибка при удалении отзыва:', error);
            }
        }
    });
});


document.addEventListener('click', (event) => {
    if (event.target.classList.contains('UpdateDeleteReviewButton')) {
        const button = event.target;
        const updateUrl = button.getAttribute('data-update-url');
        const updateId = button.getAttribute('data-update-url');
        const reviewElement = event.target.closest('.Comment');
        const commentContent = reviewElement.querySelector('.Comment-content');

        // Проверяем текст кнопки для различения действий
        if (event.target.textContent.trim() === 'редактировать') {
            // Получаем оригинальный текст
            const originalText = commentContent.textContent.trim();

            // Создаем текстовое поле и кнопки "Сохранить" и "Отмена"
            commentContent.innerHTML = `
                <textarea class="update-area-text" rows="4">${originalText}</textarea>
                <button class="save-review-button">Сохранить</button>
                <button class="cancel-review-button">Отмена</button>
            `;

            // Добавляем обработчик на кнопку "Отмена"
            reviewElement.querySelector('.cancel-review-button').addEventListener('click', () => {
                // Возвращаем оригинальный текст
                commentContent.innerHTML = originalText;
            });

            // Добавляем обработчик на кнопку "Сохранить"
            reviewElement.querySelector('.save-review-button').addEventListener('click', async () => {
                const newText = commentContent.querySelector('.update-area-text').value;

                // Логика для отправки обновленного текста на сервер
                const updateData = {
                    pk: updateId,
                    text: newText
                };
                try {
                    const response = await fetch(updateUrl, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: JSON.stringify(updateData)
                    });

                    if (response.ok) {
                        // Обновляем текст на новый
                        commentContent.innerHTML = newText;
                    } else {
                    }
                } catch (error) {
                    console.error('Ошибка при редактировании:', error);
                }
            });
        }
    }
});

// Делаем предзагрузку отзывовов во время загрузки страницы
document.addEventListener("DOMContentLoaded", () => {
    fetch(getReviews)
        .then(response => {
            if (!response.ok) {
                throw new Error('Сетевая ошибка: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            // Проверяем, что data — это объект и содержит массив results
            if (data && typeof data === 'object' && data.results && data.results.length > 0) {
                // Находим элемент заголовка
                const header = document.querySelector('.Section-header');

                // Предположим, что data.count содержит количество отзывов
                const reviewCount = data.count;
                // Находим элемент с id="main-count"
                const mainCountElement = document.getElementById('main-count');
                const smallCountElement = document.getElementById('small-count');
                // Если элемент найден, обновляем его содержимое
                if (mainCountElement) {
                    // Обновляем текст внутри элемента
                    mainCountElement.querySelector('span').textContent = `Отзывы ${reviewCount}`;
                } else {
                    console.error('Элемент с id "main-count" не найден');
                }
                if (smallCountElement) {
                    // Обновляем текст внутри элемента
                    smallCountElement.textContent = `Отзывов: ${reviewCount} шт.`;
                } else {
                    console.error('Элемент с id "small-count" не найден');
                }


                // Проходим по массиву results в обратном порядке
                for (let i = data.results.length - 1; i >= 0; i--) {
                    const review = data.results[i]; // Получаем текущий отзыв
                    const reviewId = review.pk // id отзыва

                    const userId = review.user.pk; // id пользователя
                    const userLogin = review.user.login; // Логин пользователя
                    const reviewText = review.text; // Текст отзыва

                    const updating = review.updating;
                    const createdAt = new Date(review.created_at); // Преобразуем строку даты в объект Date
                    const updateAt = new Date(review.update_at); // Здесь ты получаешь текст обновления

                    const deleteUrl = deleteReviewUrl.replace("0", reviewId);
                    const updateUrl = updateReviewUrl.replace("0", reviewId);


                    // Форматируем дату создания
                    const optionsDate = {month: 'long', day: 'numeric'}; // Опции для формата "F d"
                    const formattedDate1 = createdAt.toLocaleDateString('ru-RU', optionsDate); // Формат: "F d"

                    const formattedYear = createdAt.getFullYear(); // Формат: "Y"
                    const optionsTime = {hour: '2-digit', minute: '2-digit'}; // Опции для формата "H:i"
                    const formattedTime = createdAt.toLocaleTimeString('ru-RU', optionsTime); // Формат: "H:i"

                    // Форматируем дату обновления
                    const optionsDateUpdate = {month: 'long', day: 'numeric'}; // Опции для формата "F d"
                    const formattedDate1Update = updateAt.toLocaleDateString('ru-RU', optionsDateUpdate); // Формат: "F d"

                    const formattedYearUpdate = updateAt.getFullYear(); // Формат: "Y"
                    const optionsTimeUpdate = {hour: '2-digit', minute: '2-digit'}; // Опции для формата "H:i"
                    const formattedTimeUpdate = updateAt.toLocaleTimeString('ru-RU', optionsTimeUpdate); // Формат: "H:i"


                    const div = document.createElement('div');
                    div.className = 'Comments'; // Добавляем класс Comments

                    // Создаем новый элемент <div class="Comment">
                    const commentDiv = document.createElement('div');
                    commentDiv.className = 'Comment';

                    // Заполняем содержимое блока <div class="Comment">
                    commentDiv.innerHTML = `
                        ${updating ? `
                            <div class="update-container">
                                <p>Комментарий обновлён:</p>
                                <p>
                                    ${formattedTimeUpdate}&nbsp;/&nbsp;
                                    ${formattedDate1Update}&nbsp;/&nbsp;
                                    ${formattedYearUpdate}
                                </p>
                            </div>
                        ` : ''}
                        <div class="Comment-column Comment-column_pict">
                            <div class="Comment-avatar">
                            </div>
                        </div>
                        <div class="Comment-column">
                            <header class="Comment-header">
                                <div>
                                    <strong class="Comment-title">
                                        ${userLogin}
                                    </strong>
                                    <span class="Comment-date">
                                        ${formattedTime}&nbsp;/&nbsp;
                                        ${formattedDate1}&nbsp;/&nbsp;
                                        ${formattedYear}
                                    </span>
                                </div>
                            </header>
                            <div class="Comment-content">
                                ${reviewText}
                            </div>
                        </div>
                        ${userId === Number(current_user_id) || current_status ? `
                            <div class="User-control">
                                <button class="UpdateDeleteReviewButton"
                                        data-review-id="${reviewId}"
                                        data-update-url="${updateUrl}">
                                    редактировать
                                </button>
                                <button class="UpdateDeleteReviewButton edit-review-button"
                                        data-review-id="${reviewId}"
                                        data-delete-url="${deleteUrl}">
                                    удалить
                                </button>
                            </div>
                        ` : ''}
                    `;

                    // Вставляем <div class="Comment"> внутрь <div class="Comments">
                    div.appendChild(commentDiv);

                    // Вставляем новый элемент <div> после элемента <header>
                    header.insertAdjacentElement('afterend', div);
                }
                if (data.count > 10) {
                    // Находим нужный header
                    const createReviewHeader = document.getElementById('create-get-review');

                    if (createReviewHeader) {
                        // Создаём кнопку
                        const getMoreButton = document.createElement('button');
                        getMoreButton.className = 'download-reviews';
                        getMoreButton.textContent = 'показать ещё';
                        getMoreButton.setAttribute('next-data', data.next);

                        // Вставляем кнопку в начало <header> перед <h3>
                        createReviewHeader.insertBefore(getMoreButton, createReviewHeader.firstChild);
                    }
                }
            } else {
                const reviewCount = data.count;
                // Находим элемент с id="main-count"
                const mainCountElement = document.getElementById('main-count');
                const smallCountElement = document.getElementById('small-count');
                // Если элемент найден, обновляем его содержимое
                if (mainCountElement) {
                    // Обновляем текст внутри элемента
                    mainCountElement.querySelector('span').textContent = `Отзывы ${reviewCount}`;
                } else {
                    console.error('Элемент с id "main-count" не найден');
                }
                if (smallCountElement) {
                    // Обновляем текст внутри элемента
                    smallCountElement.textContent = `Отзывов: ${reviewCount} шт.`;
                } else {
                    console.error('Элемент с id "small-count" не найден');
                }
                const noReviewElement = document.createElement('h3');
                noReviewElement.className = 'Section-title';
                noReviewElement.id = 'no_review';
                noReviewElement.innerHTML = `
                        <p>Пока отзывов нет</p>
                        <p>Вы можете быть первым!</p>
                    `;
                const header = document.querySelector('.Section-header');
                if (header) {
                    header.insertAdjacentElement('afterend', noReviewElement);
                }
            }
        })

        .catch(error => {
            console.error('Ошибка:', error);
        });
});


document.addEventListener('click', function (event) {
    if (event.target.matches('.download-reviews')) {
        console.log('Кнопка нажата!')
        const url = event.target.getAttribute('next-data'); // Получаем URL из атрибута
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Сеть ответила с ошибкой: ' + response.status);
                }
                return response.json(); // Парсим ответ в формате JSON
            })
            .then(data => {
                console.log(data); // Выводим данные в консоль
                if (data && typeof data === 'object' && data.results && data.results.length > 0) {
                    const comments = document.querySelectorAll('.Comments');
                    const lastComment = comments[comments.length - 1];
                    for (let i = data.results.length - 1; i >= 0; i--) {
                        const review = data.results[i]; // Получаем текущий отзыв
                        const reviewId = review.pk // id отзыва

                        const userId = review.user.pk; // id пользователя
                        const userLogin = review.user.login; // Логин пользователя
                        const reviewText = review.text; // Текст отзыва

                        const updating = review.updating;
                        const createdAt = new Date(review.created_at); // Преобразуем строку даты в объект Date
                        const updateAt = new Date(review.update_at); // Здесь ты получаешь текст обновления

                        const deleteUrl = deleteReviewUrl.replace("0", reviewId);
                        const updateUrl = updateReviewUrl.replace("0", reviewId);


                        // Форматируем дату создания
                        const optionsDate = {month: 'long', day: 'numeric'}; // Опции для формата "F d"
                        const formattedDate1 = createdAt.toLocaleDateString('ru-RU', optionsDate); // Формат: "F d"

                        const formattedYear = createdAt.getFullYear(); // Формат: "Y"
                        const optionsTime = {hour: '2-digit', minute: '2-digit'}; // Опции для формата "H:i"
                        const formattedTime = createdAt.toLocaleTimeString('ru-RU', optionsTime); // Формат: "H:i"

                        // Форматируем дату обновления
                        const optionsDateUpdate = {month: 'long', day: 'numeric'}; // Опции для формата "F d"
                        const formattedDate1Update = updateAt.toLocaleDateString('ru-RU', optionsDateUpdate); // Формат: "F d"

                        const formattedYearUpdate = updateAt.getFullYear(); // Формат: "Y"
                        const optionsTimeUpdate = {hour: '2-digit', minute: '2-digit'}; // Опции для формата "H:i"
                        const formattedTimeUpdate = updateAt.toLocaleTimeString('ru-RU', optionsTimeUpdate); // Формат: "H:i"

                        const div = document.createElement('div');
                        div.className = 'Comments'; // Добавляем класс Comments

                        // Создаем новый элемент <div class="Comment">
                        const commentDiv = document.createElement('div');
                        commentDiv.className = 'Comment';

                        // Заполняем содержимое блока <div class="Comment">
                        commentDiv.innerHTML = `
                        ${updating ? `
                            <div class="update-container">
                                <p>Комментарий обновлён:</p>
                                <p>
                                    ${formattedTimeUpdate}&nbsp;/&nbsp;
                                    ${formattedDate1Update}&nbsp;/&nbsp;
                                    ${formattedYearUpdate}
                                </p>
                            </div>
                        ` : ''}
                        <div class="Comment-column Comment-column_pict">
                            <div class="Comment-avatar">
                            </div>
                        </div>
                        <div class="Comment-column">
                            <header class="Comment-header">
                                <div>
                                    <strong class="Comment-title">
                                        ${userLogin}
                                    </strong>
                                    <span class="Comment-date">
                                        ${formattedTime}&nbsp;/&nbsp;
                                        ${formattedDate1}&nbsp;/&nbsp;
                                        ${formattedYear}
                                    </span>
                                </div>
                            </header>
                            <div class="Comment-content">
                                ${reviewText}
                            </div>
                        </div>
                        ${userId === Number(current_user_id) || current_status ? `
                            <div class="User-control">
                                <button class="UpdateDeleteReviewButton"
                                        data-review-id="${reviewId}"
                                        data-update-url="${updateUrl}">
                                    редактировать
                                </button>
                                <button class="UpdateDeleteReviewButton edit-review-button"
                                        data-review-id="${reviewId}"
                                        data-delete-url="${deleteUrl}">
                                    удалить
                                </button>
                            </div>
                        ` : ''}
                    `;

                        // Вставляем <div class="Comment"> внутрь <div class="Comments">
                        div.appendChild(commentDiv);

                        // Вставляем новый элемент <div> после элемента <header>
                        lastComment.insertAdjacentElement('afterend', div);

                    }
                    const button = document.querySelector('.download-reviews');
                    if (data.next) {
                        button.setAttribute('next-data', data.next);
                    } else {
                        button.style.display = 'none';
                    }
                }

            })
            .catch(error => {
                console.error('Произошла ошибка:', error); // Обрабатываем ошибки
            });
    }
});