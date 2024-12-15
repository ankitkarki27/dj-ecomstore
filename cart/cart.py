from store.models import Product

class Cart:
    def __init__(self, request):
        """Initialize the cart."""
        self.session = request.session
        # Use 'cart' as the key to store cart data in the session
        self.cart = self.session.get('cart', {})
        self.session.modified = True  # Ensure session changes are saved

    def add(self, product, quantity=1):
        """Add a product to the cart or update its quantity."""
        product_id = str(product.id)  # Use string keys for session storage
        if product_id in self.cart:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {
                'name': product.name,
                'price': str(product.price),  # Convert price to string to avoid serialization issues
                'quantity': quantity,
            }
        self.save()

    def remove(self, product_id):
        """Remove a product from the cart."""
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
        self.save()

    def update(self, product_id, quantity):
        """Update the quantity of a product in the cart."""
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
        self.save()

    def save(self):
        """Save the cart back to the session."""
        self.session['cart'] = self.cart
        self.session.modified = True

    def clear(self):
        """Clear the cart."""
        self.session.pop('cart', None)
        self.session.modified = True

    def __len__(self):
        """Count all items in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate the total price of the cart."""
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())

    def __iter__(self):
        """Iterate over the items in the cart and fetch products from the database."""
        for product_id, item in self.cart.items():
            product = Product.objects.get(id=product_id)
            item['product'] = product
            yield item
