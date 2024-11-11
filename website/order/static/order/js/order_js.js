document.addEventListener('DOMContentLoaded', function () {
    // Вызовите toggleDeliveryOptions при загрузке страницы
    toggleDeliveryOptions();
});

function toggleDeliveryOptions() {
    const storeOptions = document.querySelector('.store_delivery_choices');
    const sellerOptions = document.querySelector('.seller_delivery_choices');
    const storePayment = document.querySelector('.store_payment');
    const sellerPayment = document.querySelector('.sellers_payments');

    const selectedType = document.querySelector('input[name="choice_delivery_type"]:checked').value;
    const deliveryContent = document.getElementById('order-info-delivery');
    const paymentContent = document.getElementById('order-info-payment');

    if (selectedType === 'store') {
        storeOptions.classList.add('show');
        storeOptions.classList.remove('hidden');
        sellerOptions.classList.add('hidden');
        sellerOptions.classList.remove('show');

        sellerPayment.classList.add('hidden');
        sellerPayment.classList.remove('show');
        storePayment.classList.add('show');
        storePayment.classList.remove('hidden');

        deliveryContent.textContent = "Доставку на себя возьмём мы";
        selectShopPaymentType()


        // Автовыбор первой опции
        selectFirstOption(storeOptions);
    } else if (selectedType === 'seller') {
        sellerOptions.classList.add('show');
        sellerOptions.classList.remove('hidden');
        storeOptions.classList.add('hidden');
        storeOptions.classList.remove('show');

        storePayment.classList.add('hidden');
        storePayment.classList.remove('show');
        sellerPayment.classList.add('show');
        sellerPayment.classList.remove('hidden');

        deliveryContent.textContent = "Доставка согласно выбранной опции у продавца(ов)";

        paymentContent.textContent = "Оплата согласно выбранной опции у продавца(ов)"; // Для продавца фиксированное сообщение

        // Автовыбор первой опции
        selectFirstOption(sellerOptions);
    }
}

function selectShopPaymentType() {
    const paymentContent = document.getElementById('order-info-payment'); // Блок для отображения типа оплаты

    const radios = document.querySelectorAll('input[name="pay"]');
    console.log(radios)
    radios.forEach(radio => {
        if (radio.checked) {
            // Находим соседний span с текстом
            const label = radio.closest('label');
            const text = label.querySelector('.toggle-text').textContent.trim();
            console.log(`Выбранный вариант: ${text}`);
            paymentContent.textContent = text;
        }
    });
}

function selectFirstOption(container) {
    const sellerBlocks = container.querySelectorAll('.seller_block');

    sellerBlocks.forEach(block => {
        const firstOption = block.querySelector('input[type="radio"]:not(:disabled)');
        if (firstOption) {
            firstOption.checked = true;
        }
    });

    const firstOptionInContainer = container.querySelector('input[type="radio"]:not(:disabled)');
    if (firstOptionInContainer) {
        firstOptionInContainer.checked = true;
    }
}

function updateOrderInfo() {
    // Получаем значение из input для ФИО
    var nameInput = document.getElementById('name');
    var orderInfoContent = document.getElementById('order-info-content');
    // Подставляем значение в блок ФИО
    orderInfoContent.textContent = nameInput.value || 'Данные не введены';

    // Получаем значение из input для телефона
    var phoneInput = document.getElementById('phone');
    var orderInfoPhone = document.getElementById('order-info-phone');
    // Подставляем значение в блок телефона
    orderInfoPhone.textContent = phoneInput.value || 'Данные не введены';

    var emailInput = document.getElementById('mail');
    var orderInfoEmail = document.getElementById('order-info-email');
    // Подставляем значение в блок E-mail
    orderInfoEmail.textContent = emailInput.value || 'Данные не введены';

    var cityInput = document.getElementById('city');
    var orderInfoCity = document.getElementById('order-info-city');
    // Подставляем значение в блок Город
    orderInfoCity.textContent = cityInput.value || 'Данные не введены';

    // Получаем значение из textarea для адреса
    var addressInput = document.getElementById('address');
    var orderInfoAddress = document.getElementById('order-info-address');
    // Подставляем значение в блок Адрес
    orderInfoAddress.textContent = addressInput.value || 'Данные не введены';
}

// Вызываем функцию сразу при загрузке страницы, чтобы синхронизировать данные
window.onload = function () {
    updateOrderInfo();  // Подставляем значение из input в блоки при загрузке
    selectShopPaymentType();
};
