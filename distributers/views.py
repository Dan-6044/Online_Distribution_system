from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category,  User, CartItem, Payment
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, ReturnItem
import json
from .models import ChatMessage
from decimal import Decimal

def logout_view(request):
    logout(request)  # Logs out the user
    return redirect('home')  # Redirect to the home page

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request, user_id=None):
    # Ensure the logged-in user matches the user_id from the URL
    if int(user_id) != request.user.id:
        return render(request, 'error.html', {'message': 'You do not have permission to view this page.'})

    user = request.user
    # Use prefetch_related to fetch OrderItems associated with each Order
    orders = Order.objects.filter(user=user).prefetch_related('items')
    
    return render(request, 'dashboard.html', {'orders': orders})


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        errors = {}

        if User.objects.filter(username=username).exists():
            errors['username'] = 'Username already taken'
        if User.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered'

        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

        # Create user and return success message
        User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({'status': 'success'})  # Success response

    return JsonResponse({'status': 'error', 'errors': {'form': 'Invalid request'}}, status=400)

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return JsonResponse({
                'status': 'success',
                'user_id': user.id  # Include the user ID in the response
            })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': {'form': 'Invalid username or password'}
            }, status=400)
    
    return render(request, 'login.html')



@login_required
def product_list(request, user_id):
    # Get the user object from the user_id
    user = get_object_or_404(User, id=user_id)

    # Fetch products and categories
    products = Product.objects.all()
    categories = Category.objects.all()

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category_id=category_filter)

    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    # Filter by rating
    rating_filter = request.GET.get('rating')
    if rating_filter:
        products = products.filter(rating__gte=rating_filter)

   

    context = {
        'products': products,
        'categories': categories,
        'star_range': range(1, 6),
        'user': user,
        
    }
    return render(request, 'products.html', context)



@login_required
def product_details(request, id):
    product = get_object_or_404(Product, id=id)
    related_products = product.category.products.exclude(id=product.id)[:4]  # Get related products excluding the current one
    return render(request, 'product_details.html', {
        'product': product,
        'related_products': related_products,
        'star_range': range(1, 6)  # Assuming you want a range of 1 to 5 stars
    })

def cart_view(request):
    # Fetch the cart items for the logged-in user
    cart_items = CartItem.objects.filter(user=request.user)

    # Calculate the total amount based on the items in the cart
    total_amount = sum(item.total_price() for item in cart_items)  # Using the method defined in the model

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
    }

    return render(request, 'cart.html', context)
@login_required
def add_to_cart(request):
    if request.method == "POST":
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        quantity = int(request.POST.get('quantity'))

        # Check if the product is already in the cart
        try:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product_name=product_name,
                defaults={'price': product_price, 'quantity': quantity}
            )
            if not created:
                # If the item exists, update the quantity
                cart_item.quantity += quantity
                cart_item.save()

            return JsonResponse({'success': True})  # Return success response
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


def update_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        cart_item.quantity = quantity
        cart_item.save()
    return redirect('cart')

def delete_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()
    return redirect('cart')
from django.db import transaction
@csrf_exempt  # Only for testing; remove in production!
def submit_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            location = data.get('location')
            phone = data.get('phone')
            cart_items = data.get('cart_items')

            if not location or not phone or not cart_items:
                return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

            # Calculate total amount
            total_amount = sum(Decimal(item['price']) * Decimal(item['quantity']) for item in cart_items)

            with transaction.atomic():
                # Create order
                order = Order.objects.create(location=location, phone=phone, user=request.user, total_amount=total_amount)

                # Create order items
                for item in cart_items:
                    OrderItem.objects.create(order=order, product_name=item['product_name'], price=item['price'], quantity=item['quantity'])

                # Clear the cart items from the database
                CartItem.objects.filter(user=request.user).delete()  # Delete all cart items for the user

            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
@csrf_exempt  # This allows the view to receive CSRF-exempt requests (you can adjust based on your needs)
def complete_payment(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        payment_method = request.POST.get('payment_method')
        amount = 99.0  # Set the amount according to your business logic

        # Retrieve the order instance
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            order_id=order.id,
            amount=amount,
            payment_method=payment_method,
            mpesa_code=request.POST.get('mpesa_code') if payment_method == 'mpesa' else None,
            card_number=request.POST.get('card_number') if payment_method == 'card' else None,
            expiry_date=request.POST.get('expiry_date') if payment_method == 'card' else None,
            cvv=request.POST.get('cvv') if payment_method == 'card' else None,
            status='completed',  # Update to 'completed' after processing payment
        )

        # Mark the payment status on the order as completed
        order.payment_status = True # Update order status to 'completed'
        order.save()

        # Add logic here for processing payment with the actual payment gateway
        # If payment succeeds, redirect user
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'errors': 'Invalid request'})

@csrf_exempt
def send_chat_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message')

        # Save the user's message in the database
        ChatMessage.objects.create(
            user=request.user,
            message=message,
            is_admin=False
        )

        return JsonResponse({'status': 'success', 'message': 'Message sent successfully.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def get_chat_messages(request):
    # Fetch all messages for the logged-in user
    user = request.user
    messages = ChatMessage.objects.filter(user=user).order_by('timestamp')

    message_list = []
    for msg in messages:
        message_list.append({
            'message': msg.message,
            'is_admin': msg.is_admin,
            'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return JsonResponse({'status': 'success', 'messages': message_list})

def get_order_items(request, order_id):
    try:
        # Fetch the order with the given order_id
        order = Order.objects.get(id=order_id)
        # Get the related items for this order
        items = order.items.all()  # Assuming the related name for OrderItem is 'items'

        # Create a list of items with required details
        item_list = [{'id': item.id, 'product_name': item.product_name, 'quantity': item.quantity} for item in items]

        # Return a JSON response
        return JsonResponse({'items': item_list})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
def return_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        item_id = request.POST.get('return_item')
        return_reason = request.POST.get('return_reason')

        # Get the order and the item to return
        order = get_object_or_404(Order, id=order_id)
        item = get_object_or_404(OrderItem, id=item_id)

        # Mark the item as returned
        item.return_status = True
        item.save()

        # Mark the order as returned if all items are returned
        if all(item.return_status for item in order.items.all()):
            order.return_status = True
            order.save()

        # Optionally, save the return details in another model (e.g., ReturnItem)
        ReturnItem.objects.create(
            order=order,
            item=item,
            reason=return_reason
        )

        # Redirect to the dashboard with the user ID
        return redirect('dashboard', user_id=request.user.id)  # Use the logged-in user's ID
