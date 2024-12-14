# cart.py
from store.models import Product

class Cart:
    def __init__(self, request):
        """Initialize the cart."""
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        """Add a product to the cart."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        self.cart[product_id]['quantity'] += quantity
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
        """Save the cart to the session."""
        self.session.modified = True

    def __iter__(self):
        """Iterate over the cart items."""
        for product_id, item in self.cart.items():
            product = Product.objects.get(id=product_id)
            item['product'] = product
            yield item

    def __len__(self):
        """Count all items in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate the total price of all items in the cart."""
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())
