from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from datetime import date
import json
from .models import Payment, Product
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.



def payments(request):
    body = json.loads(request.body)
    order_number = body['orderID']

    order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
 


    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_id=order.order_total,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct.objects.create(
            order=order,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True
        )
        product_variation = item.variations.all()
        orderproduct.variation.set(product_variation)

        product = item.product
        product.stock -= item.quantity
        product.save()

    cart_items.delete()  # Eliminar todos los elementos del carrito después de completar la orden

    data = {
        'order_number' : order.order_number,
        'transID' : payment.payment_id,
    }
    
    print(data)
    return JsonResponse(data)

def place_order(request, total=0, quantity=0):
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

    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            data = form.save(commit=False)
            data.user = current_user
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

            order_number = current_date + str(data.id)

            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
        else:
            messages.error(request, 'Por favor completa todos los campos obligatorios.')
            return redirect('checkout')
    else:
        return redirect('checkout')



def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = order.orderproduct_set.all()

        subtotal = 0
        for order_product in ordered_products:
            subtotal += order_product.product_price * order_product.quantity


        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')    