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
