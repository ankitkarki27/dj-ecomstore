$(document).ready(function () {
    $('.add-to-cart').click(function () {
        const productId = $(this).data('product-id');
        
        $.ajax({
            type: 'POST',
            url: '/cart/add/',
            data: {
                product_id: productId,
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (response) {
                alert('Product added to cart!');
                // Update cart count in the navbar
                $('#cart-count').text(response.cart_count);
            },
            error: function (xhr, errmsg, err) {
                console.error(errmsg);
                alert('Error adding product to cart!');
            }
        });
    });
});
