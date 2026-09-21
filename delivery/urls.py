from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index),
    path('open_signup', views.open_signup, name='open_signup'),
    path('open_signin', views.open_signin, name='open_signin'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('open_add_restaurant', views.open_add_restaurant, name='open_add_restaurant'),
    path('add_restaurant', views.add_restaurant, name='add_restaurant'),
    path('open_show_restaurant', views.open_show_restaurant, name='open_show_restaurant'),
    path('open_update_restaurant/<int:restaurant_id>', views.open_update_restaurant, name='open_update_restaurant'),
    path('update_restaurant/<int:restaurant_id>', views.update_restaurant, name='update_restaurant'),
    path('delete_restaurant/<int:restaurant_id>', views.delete_restaurant, name='delete_restaurant'),
    path('open_update_menu/<int:restaurant_id>', views.open_update_menu, name='open_update_menu'),
    path('update_menu/<int:restaurant_id>', views.update_menu, name='update_menu'),
    path('view_menu/<int:restaurant_id>/<str:username>', views.view_menu, name='view_menu'),

    path('add_to_cart/<int:item_id>/<str:username>', views.add_to_cart, name='add_to_cart'),
    path('show_cart/<str:username>', views.show_cart, name='show_cart'),
    path('checkout/<str:username>/', views.checkout, name='checkout'),
    path('orders/<str:username>/', views.orders, name='orders'),
    path(
    'open_add_category',
    views.open_add_category,
    name='open_add_category'
),

path(
    'add_category',
    views.add_category,
    name='add_category'
),

path(
    'show_categories',
    views.show_categories,
    name='show_categories'
),

path(
    'open_update_category/<int:category_id>',
    views.open_update_category,
    name='open_update_category'
),

path(
    'update_category/<int:category_id>',
    views.update_category,
    name='update_category'
),

path(
    'delete_category/<int:category_id>',
    views.delete_category,
    name='delete_category'
),

path(
    'open_add_delivery_partner',
    views.open_add_delivery_partner,
    name='open_add_delivery_partner'
),

path(
    'add_delivery_partner',
    views.add_delivery_partner,
    name='add_delivery_partner'
),

path(
    'show_delivery_partners',
    views.show_delivery_partners,
    name='show_delivery_partners'
),

path(
    'open_update_delivery_partner/<int:partner_id>',
    views.open_update_delivery_partner,
    name='open_update_delivery_partner'
),

path(
    'update_delivery_partner/<int:partner_id>',
    views.update_delivery_partner,
    name='update_delivery_partner'
),

path(
    'delete_delivery_partner/<int:partner_id>',
    views.delete_delivery_partner,
    name='delete_delivery_partner'
),

# Notifications

path(
    'open_add_notification',
    views.open_add_notification,
    name='open_add_notification'
),

path(
    'add_notification',
    views.add_notification,
    name='add_notification'
),

path(
    'show_notifications',
    views.show_notifications,
    name='show_notifications'
),

path(
    'delete_notification/<int:notification_id>',
    views.delete_notification,
    name='delete_notification'
),

path(
    'payment_success/<str:username>',
    views.payment_success,
    name='payment_success'
),
]