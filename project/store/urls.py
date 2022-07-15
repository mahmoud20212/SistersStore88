from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart, name='cart'),
    path('product_detail/<int:pk>', views.product_detail, name='product_detail'),
    path('add_cart/<int:pk>', views.addCart, name='add_cart'),
    path('update_cart/', views.updateCart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process_order/', views.processOrder, name='process_order'),
    path('coupon_apply/', views.coupon_apply, name='coupon_apply'),
    path('add_favorite/<int:pk>/', views.add_favorite, name='add_favorite'),
    path('favorite/', views.favorite, name='favorite'),
    path('faqs/', views.faqs, name='faqs'),
]