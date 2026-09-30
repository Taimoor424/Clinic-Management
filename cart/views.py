from django.shortcuts import render,get_object_or_404, redirect
from store.models import Medicine
from .models import Cart, CartItem, Order , OrderItem
from patient.models import Patient  # Adjust as needed
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


@login_required
def remove_from_cart(request, item_id):
    patient = get_object_or_404(Patient, user=request.user)
    cart = get_object_or_404(Cart, patient=patient)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    # Optional: return quantity to stock
    cart_item.medicine.stock += cart_item.quantity
    cart_item.medicine.save()

    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart:view_cart")

@login_required
def update_quantity(request, item_id):
    action = request.POST.get("action")
    cart = get_object_or_404(Cart, patient=request.user.patient)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    medicine = cart_item.medicine

    if action == "increase":
        if medicine.stock > 0:
            cart_item.quantity += 1
            medicine.stock -= 1
            cart_item.save()
            medicine.save()
            messages.success(request, f"Quantity increased for {medicine.name}")
        else:
            messages.warning(request, f"{medicine.name} is out of stock.")
    
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            medicine.stock += 1
            cart_item.save()
            medicine.save()
            messages.info(request, f"Quantity decreased for {medicine.name}")
        else:
            medicine.stock += 1
            medicine.save()
            cart_item.delete()
            messages.success(request, f"{medicine.name} removed from your cart.")

    return redirect("cart:view_cart")
@login_required
def add_to_cart(request, medicine_id):
    if not request.user.is_authenticated:
        return redirect('userauths:sign-in')

    patient = get_object_or_404(Patient, user=request.user)
    cart, created = Cart.objects.get_or_create(patient=patient)

    medicine = get_object_or_404(Medicine, pk=medicine_id)
    quantity = int(request.POST.get('quantity', 1))

    # Check stock
    if medicine.stock < quantity:
        messages.error(request, "Not enough stock available.")
        return redirect('store:medicine_detail', medicine_id)

    # Get or create CartItem
    cart_item, created = CartItem.objects.get_or_create(cart=cart, medicine=medicine)

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    # Reduce stock
    medicine.stock -= quantity
    medicine.save()

    messages.success(request, f"{medicine.name} added to cart.")
    return redirect("cart:view_cart")
def view_cart(request):
    patient = get_object_or_404(Patient, user=request.user)
    cart, created = Cart.objects.get_or_create(patient=patient)
    items = cart.items.select_related('medicine')
    total = cart.get_total()
    return render(request, 'cart/view_cart.html', {
        'cart': cart,
        'items': items,
        'total': total
    })



CLINIC_LOCATION = (33.6844, 73.0479)  # Example: Islamabad

def get_distance_from_clinic(address):
    geolocator = Nominatim(user_agent="hanisha_clinic")
    location = geolocator.geocode(address)
    if location:
        user_coords = (location.latitude, location.longitude)
        return geodesic(CLINIC_LOCATION, user_coords).km
    return None


@login_required
def checkout(request):
    patient = request.user.patient

    try:
        cart = Cart.objects.get(patient=patient)
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('store:store_home')

    cart_items = cart.items.all()
    subtotal = sum(item.get_subtotal() for item in cart_items)
    shipping_cost = 250
    grand_total = subtotal + shipping_cost

    if request.method == 'POST':
        # Extract form data
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        postal_code = request.POST.get('postal_code', '')
        shipping_method = request.POST.get('shipping_method', 'cod')

        if not all([first_name, last_name, email, phone, address, city]):
            messages.error(request, "Please fill out all required fields.")
            return redirect('cart:checkout')

        # Distance validation
        full_address = f"{address}, {city}"
        distance = get_distance_from_clinic(full_address)

        if distance is None:
            print("⚠️ Distance could not be calculated.")
        elif distance > 40:
            messages.error(request, "Sorry, we only deliver within 40 KM of our clinic.")
            return redirect('cart:checkout')

        # Create order with total = subtotal + shipping
        order = Order.objects.create(
            patient=patient,
            total_price=grand_total,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            shipping_method=shipping_method,
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                medicine=item.medicine,
                quantity=item.quantity,
                price=item.medicine.price
            )

        # Clear cart
        cart.items.all().delete()

        # Send confirmation email
        try:
            send_mail(
                subject=f"Order Confirmation - Order #{order.id}",
                message=(
                    f"Hello {order.first_name},\n\n"
                    f"Your order #{order.id} has been successfully placed.\n"
                    f"Total: Rs. {order.total_price}\n"
                    f"Shipping Method: {order.get_shipping_method_display()}\n"
                    f"Delivery Address: {order.address}, {order.city}\n\n"
                    f"Thank you for shopping with Hanisha Homeo Clinic!"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            print("✅ Email sent successfully")
        except Exception as e:
            print("❌ Email sending failed:", e)
            messages.warning(request, "Order placed, but confirmation email failed to send.")

        messages.success(request, "Your order has been placed!")
        return redirect('store:store_home')

    return render(request, 'cart/checkout.html', {
        'cart_items': cart_items,
        'total': subtotal,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total,
        'shipping_method': request.POST.get('shipping_method', 'cod')
    })