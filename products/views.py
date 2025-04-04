from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import Product, Cart, CartItem
from .forms import ProductForm
import stripe
from django.conf import settings
from stripe.error import StripeError
from django.views.decorators.http import require_POST

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                
                # Create Stripe product
                stripe_product = stripe.Product.create(
                    name=product.name,
                    description=product.description
                )
                
                # Create Stripe price
                stripe_price = stripe.Price.create(
                    product=stripe_product.id,
                    unit_amount=int(product.price * 100),  # Convert to cents
                    currency='usd'
                )
                
                product.stripe_product_id = stripe_product.id
                product.stripe_price_id = stripe_price.id
                product.save()
                
                messages.success(request, 'Product created successfully!')
                return redirect('product_list')
            except StripeError as e:
                messages.error(request, f'Stripe API Error: {str(e)}')
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {str(e)}')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            try:
                updated_product = form.save(commit=False)
                
                # Update Stripe product
                stripe.Product.modify(
                    product.stripe_product_id,
                    name=updated_product.name,
                    description=updated_product.description
                )
                
                # Update Stripe price
                stripe.Price.modify(
                    product.stripe_price_id,
                    active=False
                )
                
                # Create new price
                new_price = stripe.Price.create(
                    product=product.stripe_product_id,
                    unit_amount=int(updated_product.price * 100),
                    currency='usd'
                )
                
                updated_product.stripe_price_id = new_price.id
                updated_product.save()
                
                messages.success(request, 'Product updated successfully!')
                return redirect('product_list')
            except StripeError as e:
                messages.error(request, f'Stripe API Error: {str(e)}')
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {str(e)}')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            # Archive Stripe product
            stripe.Product.modify(
                product.stripe_product_id,
                active=False
            )
            product.delete()
            messages.success(request, 'Product deleted successfully!')
            return redirect('product_list')
        except StripeError as e:
            messages.error(request, f'Stripe API Error: {str(e)}')
            return redirect('product_list')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')
            return redirect('product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_key)
    return cart

@require_POST
def add_to_cart(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
        return JsonResponse({'status': 'success', 'cart_total': cart.total})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def remove_from_cart(request, item_id):
    try:
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.delete()
        messages.success(request, 'Item removed from cart!')
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def view_cart(request):
    cart = get_or_create_cart(request)
    return render(request, 'products/cart.html', {'cart': cart})

def checkout(request):
    try:
        cart = get_or_create_cart(request)
        
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty!')
            return redirect('products:view_cart')
        
        # Create Stripe Checkout Session
        line_items = [{
            'price': item.product.stripe_price_id,
            'quantity': item.quantity,
        } for item in cart.items.all()]
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('products:checkout_success')),
            cancel_url=request.build_absolute_uri(reverse('products:view_cart')),
        )
        
        return redirect(checkout_session.url)
    except StripeError as e:
        messages.error(request, f'Stripe Error: {str(e)}')
        return redirect('products:view_cart')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('products:view_cart')

def checkout_success(request):
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'Payment successful! Thank you for your purchase.')
    return redirect('products:product_list')
