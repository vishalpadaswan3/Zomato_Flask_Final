// JavaScript code for Zesty Zomato web application

// Example function to confirm deletion of a dish
function confirmDelete(dishId) {
    if (confirm("Are you sure you want to delete this dish?")) {
        // Send a POST request to delete the dish
        fetch(`/menu/delete/${dishId}`, {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                alert("Dish deleted successfully!");
                location.reload(); // Refresh the page
            } else {
                alert("Failed to delete dish.");
            }
        })
        .catch(error => {
            console.log(error);
            alert("An error occurred while deleting the dish.");
        });
    }
}

// Example function to update the status of an order
function updateOrderStatus(orderId, newStatus) {
    // Send a POST request to update the order status
    fetch(`/orders/update/${orderId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => {
        if (response.ok) {
            alert("Order status updated successfully!");
            location.reload(); // Refresh the page
        } else {
            alert("Failed to update order status.");
        }
    })
    .catch(error => {
        console.log(error);
        alert("An error occurred while updating the order status.");
    });
}
