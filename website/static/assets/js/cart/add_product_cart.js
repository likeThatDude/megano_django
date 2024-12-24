// Добавляем функционал добавления товара
document.addEventListener('DOMContentLoaded', async function() {
    const addProductButtons = document.querySelectorAll('.btn-add-to-cart');
    addProductButtons.forEach(addButton => {
        addButton.addEventListener('click', async function(event) {
            event.preventDefault();
            const dataAddButton = await getDataFromButton(addButton);
            await postAPICart(dataAddButton);
            await updateTotalQuanCost();
        })
    })
})
