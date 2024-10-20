from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()  # Inventory Management
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return self.product_name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_status = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False) 
    

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    return_status = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.product_name} - {self.quantity} pcs"
    

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20)  # 'card' or 'mpesa'
    mpesa_code = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=20, blank=True, null=True)
    expiry_date = models.CharField(max_length=5, blank=True, null=True)  # MM/YY format
    cvv = models.CharField(max_length=4, blank=True, null=True)
    status = models.CharField(max_length=10, default='pending')  # 'pending' or 'completed'

    def __str__(self):
        return f'Payment {self.id} - {self.status} by {self.user.username}'
    
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_admin = models.BooleanField(default=False)  # True if the message is from the admin
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)  # To link replies
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user.username} at {self.timestamp}"
    
class ReturnItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    reason = models.TextField()
    return_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return of {self.item.product_name} from Order {self.order.id}"
