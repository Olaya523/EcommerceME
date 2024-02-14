from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order
from datetime import date

# Create your views here.


def place_order(request, total = 0, quantity = 0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    
    tax = (2*total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            today_date = date.today()
            yr = int(today_date.strftime('%Y'))
            mt = int(today_date.strftime('%m'))
            dt = int(today_date.strftime('%d'))
            d = date(yr, mt, dt)
            current_date = d.strftime("%y%m%d")

            order_numer = current_date + str(data.id)
                        # Suponiendo que 'data' es una instancia de un modelo que tiene un campo 'order_number'
            # Aquí estás concatenando la fecha actual con el ID de 'data' para formar el número de pedido
            order_number = current_date + str(data.id)

            # Guardar el número de pedido en el campo 'order_number' de 'data'
            data.order_number = order_number
            return redirect('checkout')
    else:
        return redirect('checkout')


