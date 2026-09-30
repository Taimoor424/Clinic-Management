from django.shortcuts import render,get_object_or_404
from .models import Medicine
from cart.models import Cart, CartItem
from patient.models import Patient

def store_home(request):
    medicines = Medicine.objects.all()
    return render(request, 'store/store_home.html', {'medicines': medicines})


def medicine_detail(request, medicine_id):
    medicine = get_object_or_404(Medicine, pk=medicine_id)
    cart_items = []

    if request.user.is_authenticated:
        try:
            patient = Patient.objects.get(user=request.user)
            cart = Cart.objects.get(patient=patient)
            cart_items = cart.items.all()
        except:
            cart_items = []

    return render(request, 'store/medicine_detail.html', {
        'medicine': medicine,
        'cart_items': cart_items
    })
