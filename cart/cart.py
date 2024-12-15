# cart.py
from store.models import Product

class Cart:
   def __init__(self,request):
        self.session = request.session
        #get the current session key if it exists,key is session_key
        cart=self.session.get('session_key')
       
       #if the user is new,no session key! so create one
        if 'session_key' not in request.session:
         cart =self.session['session_key']={}
           
        #make sure cart is available on allpage of site
         self.cart = cart
         
def add(self,product):
        product_id =str(product.id)
        
        #logic
        if product_id in self.cart:
            pass
        else:
            self.cart[product_id]={'price':str(product.price)}
        
        self.session.modified=True