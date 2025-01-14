<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

    $(document).ready(function () {
        // Remove product from cart
        $(".remove-item").click(function () {
            const productId = $(this).data("product-id");
            $.ajax({
                url: "{% url 'cart:cart_delete' %}",
                method: "POST",
                data: {
                    product_id: productId,
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                },
                success: function (response) {
                    if (response.success) {
                        $(`#cart-item-${productId}`).remove();
                        $("#total-amount").text(`Rs${response.cart_total}`);
                        if (response.cart_total === 0) {
                            $("#cart-items").html(`
                                <tr>
                                    <td colspan="6" class="text-center py-6 text-gray-500">Your cart is empty.</td>
                                </tr>
                            `);
                        }
                    } else {
                        alert(response.message);
                    }
                },
                error: function () {
                    alert("An error occurred while removing the product.");
                }
            });
        });

        $(".quantity-input").change(function () {
            const productId = $(this).data("product-id");
            const newQuantity = $(this).val();
            if (newQuantity < 1) return; // Prevent invalid quantity
        
            $.ajax({
                url: "{% url 'cart:cart_update' %}",
                method: "POST",
                data: {
                    product_id: productId,
                    quantity: newQuantity,
                    csrfmiddlewaretoken: '{{ csrf_token }}', // Ensure CSRF token is passed
                },
                success: function (response) {
                    if (response.success) {
                        $(`#cart-item-${productId} .item-total`).text(`Rs${response.item_total}`);
                        $("#total-amount").text(`Rs${response.cart_total}`);
                    } else {
                        alert(response.message);
                    }
                },
                error: function () {
                    alert("An error occurred while updating the quantity.");
                }
            });
        });
      
    
    });
