from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product
from .forms import ProductForm
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
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
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
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
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        # Archive Stripe product
        stripe.Product.modify(
            product.stripe_product_id,
            active=False
        )
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})
