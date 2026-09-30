from django.db import models
from store.models import Medicine  
from patient.models import Patient  
from django.utils import timezone

class Cart(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.patient.full_name}"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.medicine.name} ({self.quantity})"

    def get_subtotal(self):
        return self.medicine.price * self.quantity
    
class Order(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🧾 Billing & Delivery Info
    first_name = models.CharField(max_length=100, default='John')
    last_name = models.CharField(max_length=100, default='Doe')
    email = models.EmailField(default='example@example.com')
    phone = models.CharField(max_length=20, default='0000000000')
    address = models.CharField(max_length=255, default='N/A')
    city = models.CharField(max_length=100, default='Unknown')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, null=False, blank=False)


    # 📦 Shipping Method
    shipping_method = models.CharField(
        max_length=50,
        choices=[('prepaid', 'Prepaid'), ('cod', 'Cash on Delivery')],
        default='prepaid'
    )
    ORDER_STATUS = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Pending')
    @property
    def created_date(self):
        return self.created_at.strftime('%Y-%m-%d') if self.created_at else "N/A"
    def __str__(self):
        return f"Order #{self.id} by {self.patient.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.medicine.name}"
