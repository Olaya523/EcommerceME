from django.shortcuts import render, redirect
from .forms import  RegistrationForm
from .models import Account
from  django.contrib import messages, auth
from  django.contrib.auth.decorators import login_required
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests

# Create your views here.
def register(request):
        form = RegistrationForm()
        
        if request.method == 'POST':
                form = RegistrationForm(request.POST)
                if  form.is_valid():
                        first_name = form.cleaned_data['first_name']
                        last_name = form.cleaned_data['last_name']   
                        phone_number = form.cleaned_data['phone_number']
                        email = form.cleaned_data['email']
                        password = form.cleaned_data['password']

                        username =   email.split("@")[0]
                        user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
                        user.phone_number = phone_number
                        user.save( )
        context = {
                'form': form

        }
        return render(request, 'accounts/register.html', context)

def login(request):
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            user =  auth.authenticate(email=email, password=password)
            if user is not None:
                
                try:
                        cart = Cart.objects.get(_cart_id=_cart_id(request))
                        is_car_items_exist = CartItem.objects.filter(cart=cart).exists()
                        if is_car_items_exist:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                        item.user = user
                                        item.save()
                except:
                       pass        


                auth.login(request, user)
                messages.error(request, 'Ha iniciado sesion correctamente')

                url = request.META.get('HTTP_REFERER')
                try:
                        query = requests.utils.urlparse(url).query
                        params = dict(x.split('=') for x in query.split('&'))
                        if 'next' in params:
                              nextPage = params['next']
                              return redirect(nextPage)
                except:
                       return redirect('home')

            else:
                messages.error(request, 'Las credenciales son incorrectas')
                return redirect('login')

        return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
        auth.logout(request)
        messages.success(request, 'Has cerrado sesion ')
        return redirect('login')