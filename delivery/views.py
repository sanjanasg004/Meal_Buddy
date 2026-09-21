from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from .models import Cart, Customer, Item, Restaurant, Category, DeliveryPartner, Notification, Order, OrderItem

import razorpay
from django.conf import settings

# Create your views here.
def index(request):
    return render(request, "delivery/index.html")

def open_signup(request):
    return render(request, "delivery/signup.html")

def open_signin(request):
    return render(request, "delivery/signin.html")

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')


        try:
            Customer.objects.get(username = username)
            return HttpResponse("Duplicate username!")
        except:
            Customer.objects.create(
                username = username,
                password = password,
                email = email,
                mobile = mobile,
                address = address,
            )
    return render(request, 'delivery/signin.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

    try:
        Customer.objects.get(username = username, password = password)
        if username == 'admin':
            return render(request, 'delivery/admin_home.html')
        else:
            restaurantList = Restaurant.objects.all()
            return render(request, 'delivery/customer_home.html', {"restaurantList" : restaurantList, "username" : username})
    except Customer.DoesNotExist:
        return render(request, 'delivery/fail.html')

def open_add_restaurant(request):
    return render(request, 'delivery/add_restaurant.html')

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        try:
            Restaurant.objects.get(name = name)
            return HttpResponse("Duplicate restaurant!")
        except:
            Restaurant.objects.create(
                name = name,
                picture = picture,
                cuisine = cuisine,
                rating = rating,
            )
    return render(request, 'delivery/admin_home.html')

def open_show_restaurant(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html', {'restaurantList': restaurantList})

def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'delivery/update_restaurant.html', {"restaurant": restaurant}) 

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating

        restaurant.save()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})

def delete_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    restaurant.delete()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})

def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)
    itemList = restaurant.items.all()
    categoryList = Category.objects.filter(is_active=True)

    return render(
        request,
        'delivery/update_menu.html',
        {
            "itemList": itemList,
            "restaurant": restaurant,
            "categoryList": categoryList
        }
    )

def update_menu(request, restaurant_id):

    restaurant = Restaurant.objects.get(id=restaurant_id)

    if request.method == 'POST':

        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegeterian = request.POST.get('vegeterian') == 'on'
        picture = request.POST.get('picture')
        category_id = request.POST.get('category')

        try:

            Item.objects.get(
                name=name,
                restaurant=restaurant
            )

            return HttpResponse("Duplicate item!")

        except Item.DoesNotExist:

            category = Category.objects.get(id=category_id)

            Item.objects.create(
                restaurant=restaurant,
                category=category,
                name=name,
                description=description,
                price=price,
                vegeterian=vegeterian,
                picture=picture,
            )

    return redirect(
        'open_update_menu',
        restaurant_id=restaurant.id
    )

def view_menu(request, restaurant_id, username):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    #itemList = Item.objects.all()
    return render(request, 'delivery/customer_menu.html'
                  ,{"itemList" : itemList,
                     "restaurant" : restaurant, 
                     "username":username})

def add_to_cart(request, item_id, username):
    item = Item.objects.get(id = item_id)
    customer = Customer.objects.get(username = username)

    cart, created = Cart.objects.get_or_create(customer = customer)

    cart.items.add(item)

    return HttpResponse('added to cart')

def show_cart(request, username):
    customer = Customer.objects.get(username = username)
    cart = Cart.objects.filter(customer=customer).first()
    items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    return render(request, 'delivery/cart.html',{"itemList" : items, "total_price" : total_price, "username":username})

def checkout(request, username):
    # Fetch customer and their cart
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    if total_price == 0:
        return render(request, 'delivery/checkout.html', {
            'error': 'Your cart is empty!',
        })

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay order
    order_data = {
        'amount': int(total_price * 100),  # Amount in paisa
        'currency': 'INR',
        'payment_capture': '1',  # Automatically capture payment
    }
    order = client.order.create(data=order_data)

    # Pass the order details to the frontend
    return render(request, 'delivery/checkout.html', {
        'username': username,
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],  # Razorpay order ID
        'amount': total_price,
    })

def orders(request, username):

    customer = get_object_or_404(
        Customer,
        username=username
    )

    order_list = Order.objects.filter(
        customer=customer
    ).prefetch_related(
        'items__item'
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'delivery/orders.html',
        {
            'username': username,
            'customer': customer,
            'order_list': order_list
        }
    )

def show_categories(request):
    categoryList = Category.objects.all()
    return render(
        request,
        'delivery/show_categories.html',
        {'categoryList': categoryList}
    )

def open_add_category(request):
    return render(request, 'delivery/add_category.html')

def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.POST.get('image')
        description = request.POST.get('description')

        try:
            Category.objects.get(name=name)
            return HttpResponse("Duplicate category!")

        except Category.DoesNotExist:
            Category.objects.create(
                name=name,
                image=image,
                description=description
            )

    return render(request, 'delivery/admin_home.html')

def open_update_category(request, category_id):
    category = Category.objects.get(id=category_id)

    return render(
        request,
        'delivery/update_category.html',
        {'category': category}
    )

def update_category(request, category_id):
    category = Category.objects.get(id=category_id)

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.image = request.POST.get('image')
        category.description = request.POST.get('description')
        category.is_active = request.POST.get('is_active') == 'on'

        category.save()

    categoryList = Category.objects.all()

    return render(
        request,
        'delivery/show_categories.html',
        {'categoryList': categoryList}
    )

def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)

    category.delete()

    categoryList = Category.objects.all()

    return render(
        request,
        'delivery/show_categories.html',
        {'categoryList': categoryList}
    )

def open_add_delivery_partner(request):

    return render(
        request,
        'delivery/add_delivery_partner.html'
    )

def add_delivery_partner(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        vehicle_type = request.POST.get('vehicle_type')
        license_number = request.POST.get('license_number')
        status = request.POST.get('status')

        try:

            DeliveryPartner.objects.get(
                license_number=license_number
            )

            return HttpResponse(
                "Delivery partner with this license already exists!"
            )

        except DeliveryPartner.DoesNotExist:

            DeliveryPartner.objects.create(
                name=name,
                mobile=mobile,
                vehicle_type=vehicle_type,
                license_number=license_number,
                status=status
            )

            return redirect(
                'show_delivery_partners'
            )

    return redirect(
        'open_add_delivery_partner'
    )

def show_delivery_partners(request):

    deliveryPartners = DeliveryPartner.objects.all()

    return render(
        request,
        'delivery/show_delivery_partners.html',
        {
            'deliveryPartners': deliveryPartners
        }
    )

def open_update_delivery_partner(request, partner_id):

    partner = DeliveryPartner.objects.get(id=partner_id)

    return render(
        request,
        'delivery/update_delivery_partner.html',
        {
            'partner': partner
        }
    )

def update_delivery_partner(request, partner_id):

    partner = DeliveryPartner.objects.get(id=partner_id)

    if request.method == 'POST':

        partner.name = request.POST.get('name')
        partner.mobile = request.POST.get('mobile')
        partner.vehicle_type = request.POST.get('vehicle_type')
        partner.license_number = request.POST.get('license_number')
        partner.assigned_orders = request.POST.get('assigned_orders')
        partner.status = request.POST.get('status')

        partner.save()

        return redirect('show_delivery_partners')

    return render(
        request,
        'delivery/update_delivery_partner.html',
        {
            'partner': partner
        }
    )

def delete_delivery_partner(request, partner_id):

    partner = DeliveryPartner.objects.get(id=partner_id)

    partner.delete()

    return redirect('show_delivery_partners')

# ==========================================
# NOTIFICATIONS
# ==========================================

def open_add_notification(request):

    return render(
        request,
        'delivery/add_notification.html'
    )

def add_notification(request):

    if request.method == 'POST':

        title = request.POST.get('title')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type')

        customers = Customer.objects.exclude(
            username='admin'
        )

        for customer in customers:

            Notification.objects.create(
                title=title,
                message=message,
                notification_type=notification_type,
                customer=customer
            )

        return redirect('show_notifications')

    return redirect('open_add_notification')

def show_notifications(request):

    notifications = Notification.objects.select_related(
        'customer'
    ).order_by('-created_at')

    return render(
        request,
        'delivery/show_notifications.html',
        {
            'notifications': notifications
        }
    )

def delete_notification(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id
    )

    notification.delete()

    return redirect('show_notifications')

def payment_success(request, username):

    customer = get_object_or_404(
        Customer,
        username=username
    )

    cart = Cart.objects.filter(
        customer=customer
    ).first()

    if not cart:
        return render(
            request,
            'delivery/fail.html'
        )

    cart_items = cart.items.all()

    if not cart_items.exists():
        return render(
            request,
            'delivery/fail.html'
        )

    total_price = cart.total_price()

    # Create Order
    order = Order.objects.create(
        customer=customer,
        total_price=total_price,
        delivery_address=customer.address,
        status='Pending'
    )

    # Create Order Items
    for item in cart_items:

        OrderItem.objects.create(
            order=order,
            item=item,
            quantity=1,
            price=item.price
        )

    # Clear cart
    cart.items.clear()

    # Create notification
    Notification.objects.create(
        title='Order Placed Successfully 🎉',
        message=f'Your Order #{order.id} has been placed successfully.',
        notification_type='Order Update',
        customer=customer
    )

    return render(
        request,
        'delivery/order_success.html',
        {
            'order': order,
            'username': username
        }
    )