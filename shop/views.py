# shop/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from .models import Product, CartItem, Order, OrderItem
from .forms import CheckoutForm

def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аккаунт создан. Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/profile.html', {'orders': orders})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Проверяем, есть ли уже этот товар в корзине
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    # Если товар уже был в корзине, обновляем количество
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'"{product.name}" добавлен в корзину.')
    return redirect('home')

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in cart_items)
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        messages.warning(request, 'Ваша корзина пуста.')
        return redirect('cart')
    
    total = sum(item.get_total_price() for item in cart_items)
    form = CheckoutForm()
    
    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'form': form
    })

@login_required
def place_order(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cart_items = CartItem.objects.filter(user=request.user)
            if not cart_items:
                messages.warning(request, 'Ваша корзина пуста.')
                return redirect('cart')
            
            total = sum(item.get_total_price() for item in cart_items)
            
            # Создаем заказ
            order = Order.objects.create(
                user=request.user,
                total_price=total,
                name=form.cleaned_data['name'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone']
            )
            
            # Добавляем товары в заказ
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # Очищаем корзину
            cart_items.delete()
            
            return redirect('order_confirmation')
    
    return redirect('checkout')

@login_required
def order_confirmation(request):
    return render(request, 'shop/order_confirmation.html')
