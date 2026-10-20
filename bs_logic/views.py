from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CheckoutForm, SignUpForm
from .models import Category, Order, OrderItem, Product

def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('product_list')

    return render(request, 'registration/signup.html', {'form': form})

def product_list(request):
    products = Product.objects.filter(in_stock=True).select_related('category')
    cat = request.GET.get('category')
    if cat:
        products = products.filter(category_id=cat)
    return render(request, 'bs_logic/product_list.html', {
        'products': products, 
        'categories': Category.objects.all(),
    })

# Cart (stored in session: {product_id:kg})
def _cart_items(cart):
    items, total = [], Decimal('0')
    for p in Product.objects.filter(id__in=cart.keys(), in_stock=True):
        qty = Decimal(cart[str(p.id)])
        sub = p.price_per_kg * qty
        items.append({'product': p, 'qty': qty, 'subtotal': sub})
        total += sub
    return items, total

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, in_stock=True)
    try:
        qty = Decimal(request.POST.get('quantity', '1'))
        if qty < Decimal('0,25') or qty > 100:
            raise InvalidOperation
    except InvalidOperation:
        messages.error(request, 'Enter a valid quantity in kg (minimum 0.25).')
        return redirect('product_list')
    cart = request.session.get('cart', {})
    current = Decimal(cart.get(str(product.id), '0'))
    cart[str(product.id)] = str(current + qty)
    request.session['cart'] = cart
    messages.success(request, f'Added {qty} kg of {product.name}.')
    return redirect('product_list')

def cart_detail(request):
    items, total = _cart_items(request.session.get('cart', {}))
    return render(request, 'bs_logic/cart.html', {'items': items, 'total': total})


@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart_detail')

@login_required
def checkout(request):
        cart = request.session.get('cart', {})
        items, total = _cart_items(cart)
        if not items:
            messages.info(request, 'Your cart is empty.')
            return redirect('product_list')

        profile = getattr(request.user, 'profile', None)
        initial = {'phone': getattr(profile, 'phone', ''),
               'delivery_address': getattr(profile, 'address', '')}
        form = CheckoutForm(request.POST or None, initial=initial)

        if request.method == 'POST' and form.is_valid():
            with transaction.atomic():
                order = Order.objects.create(user=request.user, **form.cleaned_data)
                OrderItem.objects.bulk_create([
                    OrderItem(order=order, product=i['product'],
                              quantity_kg=i['qty'], unit_price=i['product'].price_per_kg)
                    for i in items
                ])
            request.session['cart'] = {}
            messages.success(request, f'Order #{order.pk} placed. We will contact you to confirm.')
            return redirect('order_history')

        return render(request, 'bs_logic/checkout.html', {'form': form, 'items': items, 'total': total})


@login_required
def order_history(request):
    orders = request.user.orders.prefetch_related('items__product')
    return render(request, 'bs_logic/order_history.html', {'orders': orders})