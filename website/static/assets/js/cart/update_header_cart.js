// Функция для обновления данных в хедере страницы (header.html)
async function updateTotalQuanCost() {
    const elemTotalQuantityProducts = document.querySelector('.CartBlock-amount');
    const elemTotalCostProducts = document.querySelector('.CartBlock-cost');

    const dataCart = await getAPICart();
    elemTotalQuantityProducts.innerText = dataCart.total_quantity;
    elemTotalCostProducts.innerText = dataCart.total_cost;
}

// Выполняем обновление при полной загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    updateTotalQuanCost(); // Вызываем функцию для обновления количества в корзине
});