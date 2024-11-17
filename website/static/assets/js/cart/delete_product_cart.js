// Добавляем функционал удаления товара
document.addEventListener('DOMContentLoaded', async function() {
    const productCards = document.querySelectorAll('.ProductCard');
    productCards.forEach(productCard => {
        const removeButton = productCard.querySelector('a.btn.btn_primary')
        removeButton.addEventListener('click', async function(event) {
            event.preventDefault();
            const data = {"product_id": productCard.dataset.product_id};
            await deleteAPICart(data);
            await updateTotalQuanCost();
            productCard.remove()
        });
    });
});
