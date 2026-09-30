from django.contrib import admin
from .models import Cart, CartItem
from .models import Order, OrderItem

admin.site.register(Cart)
admin.site.register(CartItem)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('medicine', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'created_at')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'medicine', 'quantity', 'price')
    list_filter = ('medicine',)