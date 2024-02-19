from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from datetime import date
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse

# Create your views here.



def payments(request):
    body = json.loads(request.body)
    print(body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

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

    mail_subject = 'Gracias por tu compra'
    body = render_to_string('orders/order_recieved_email.html', {
        'user': request.uer,
        'order': order,
    })

    to_email = request.user.email
    send_email = EmailMessage(mail_subject,body, to=[to_email])
    send_email.send()

    data = {
        'order_number' : order.order_number,
        'transID' : payment.payment_id,
    }
    
    return JsonResponse(data)

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

            order_number = current_date + str(data.id)

            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')



def order_complete(request):
    return render(request, 'orders/order_complete.html')
    