import string  
import secrets # import package 
import json
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
from .models import Cart, Product, Category, Order, OrderDone, Favorite, Coupon, FAQ
from django.contrib.auth.models import User
from .forms import NewComment, ContactForm
from django.views import View
from webpush import send_user_notification

# ============================================

def cart_items(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        return order.get_cart_items

def favorite_number(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        favorite = Favorite.objects.get(customer=customer)
        product = favorite.product.all().count()
        return product
    return 0

# ============================================

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = 'http://127.0.0.1:8000/'

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        # price = Price.objects.get(id=self.kwargs["pk"])
        YOUR_DOMAIN = "http://127.0.0.1:8000"  # change in production
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': 200,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return redirect(checkout_session.url)

def index(request):
    products = Product.objects.all().order_by('?')[:12]
    context = {
        'products': products,
        'cart_items': cart_items(request),
        'favorite_number': favorite_number(request),
    }
    return render(request, 'store/index.html', context)

def faqs(request):
    faqs = FAQ.objects.all()

    # paginator
    paginator = Paginator(faqs, 5)
    page = request.GET.get('page')
    try:
        faqs = paginator.page(page)
    except PageNotAnInteger:
        faqs = paginator.page(1)
    except EmptyPage:
        faqs = paginator.page(paginator.num_page)

    context = {
        'faqs': faqs,
        'cart_items': cart_items(request),
        'favorite_number': favorite_number(request),
    }
    return render(request, 'store/faqs.html', context)

def about(request):
    context = {
        'cart_items': cart_items(request),
        'favorite_number': favorite_number(request),
    }
    return render(request, 'store/about.html', context)

def contact(request):
    success = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
    else:
        form = ContactForm()

    context = {
        'form': form,
        'cart_items': cart_items(request),
        'favorite_number': favorite_number(request),
        'success': success,
    } 
    return render(request, 'store/contact.html', context)
    
def product_list(request):
    # filter
    category = request.GET.get('category')
    color = request.GET.get('color')
    price = request.GET.get('price')
    sort = request.GET.get('sort')
    status = request.GET.get('status')
    tag = request.GET.get('tag')
    if sort == 'l2h':
        products = Product.objects.order_by('price')
    elif sort == 'h2l':
        products = Product.objects.order_by('-price')
    elif price == '50':
        products = Product.objects.filter(price__lt=50)
    elif price == '100':
        products = Product.objects.filter(Q(price__gte=50) & Q(price__lt=100))
    elif price == '150':
        products = Product.objects.filter(Q(price__gte=100) & Q(price__lt=150))
    elif price == '200':
        products = Product.objects.filter(Q(price__gte=150) & Q(price__lt=200))
    elif price == '201':
        products = Product.objects.filter(price__gte=200)
    elif status == 'new':
        products = Product.objects.filter(status='New')
    elif category != None:
        products = Product.objects.filter(category__name=category)
    elif color != None:
        products = Product.objects.filter(color__color=color)
    elif tag != None:
        products = Product.objects.filter(tags__tag=tag)
    else:
        products = Product.objects.all()

    # search
    if 'search' in request.GET:
        product = request.GET.get('search')
        if product:
            products = Product.objects.filter(name__icontains=product)

    # paginator
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_page)

    # category
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'page': page,
        'cart_items': cart_items(request),
        'favorite_number': favorite_number(request),
    }
    return render(request, 'store/product.html', context)

@login_required(login_url='login')
def cart(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.cart_set.all()    
    
    context = {
        'order': order,
        'items': items,
        'cart_items': cart_items(request),
        'favorite_number': favorite_number(request),
    }
    return render(request, 'store/cart.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Favorite
    if request.user.is_authenticated:
        customer = request.user.customer
        favorite_bool = Favorite.objects.filter(customer=customer, product=product).exists()
    else:
        favorite_bool = False
    
    count = product.comments.filter(active=True).count()
    comments = product.comments.filter(active=True)
    if request.method == 'POST':
        comment_form = NewComment(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.product = product
            new_comment.save()
            messages.success(request, 'شكرا لك... سيتم نشر تعليقك بعد المراجعة.')
            return HttpResponseRedirect(reverse('product_detail', args=[pk]))
        else:
            messages.warning(request, 'المعلومات التي ادخلتها غير صالحه الرجاء محاوله مرة آخرى.')
        #     return HttpResponseRedirect(reverse('product_detail', args=[pk]))
    else:
        comment_form = NewComment()

    # paginator
    paginator = Paginator(comments, 5)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_page)


    context = {
        'product': product,
        'cart_items': cart_items(request),
        'comments': comments,
        'form': comment_form,
        'count': count,
        'favorite_number': favorite_number(request),
        'favorite_bool': favorite_bool,
    }
    return render(request, 'store/product_detail.html', context)

@login_required(login_url='login')
def addCart(request, pk):
    if request.method == 'POST':
        id = pk
        product = Product.objects.get(id=id)
        if product.status == 'Ended':
            messages.warning(request, 'لا يمكن إضافة المنتج لعربة التسوق لانه قد انتهى.')
            return HttpResponseRedirect(reverse('product_detail', args=[id]))
            
        size = request.POST.get('size')
        color = request.POST.get('color')
        if size == None or color == None:
            messages.warning(request, 'الرجاء تحديد المقاس و اللون.')
            return HttpResponseRedirect(reverse('product_detail', args=[id]))

        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cart_item, created = Cart.objects.get_or_create(order=order, product=product, size=size, color=color)
        cart_item.quantity = (cart_item.quantity + 1)
        cart_item.save()
        messages.success(request, 'تمت الإضافة الى عربة التسوق بنجاح.')
        return HttpResponseRedirect(reverse('product_detail', args=[id]))
    else:
        return HttpResponseRedirect(reverse('product_detail', args=[pk]))

@login_required(login_url='login')
def updateCart(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']
    size = data['size']
    color = data['color']

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    cart_item, created = Cart.objects.get_or_create(order=order, product=product, size=size, color=color)

    if action == 'add':
        cart_item.quantity = (cart_item.quantity + 1)
    elif action == 'remove':
        cart_item.quantity = (cart_item.quantity - 1)

    cart_item.save()

    if cart_item.quantity <= 0:
        cart_item.delete()

    if action == 'delete':
        cart_item.delete()
    
    
    return JsonResponse('Item was added', safe=False)

@login_required(login_url='login')
def checkout(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    cart = Cart.objects.filter(order=order).exists()
    if cart:

        if not customer.phone_number or not customer.location or not request.user.first_name or not request.user.last_name:
            messages.warning(request, 'الرجاء تعبئة الحقول الفارغة.')
            return HttpResponseRedirect(reverse('profile'))
        else:
            items = order.cart_set.all()
            context = {
                'order': order,
                'items': items,
                'cart_items': cart_items(request),
                'favorite_number': favorite_number(request),
            }
    else:
        messages.warning(request, 'عربة التسوق فارغة لا يمكن إجارء العملية.')
        return HttpResponseRedirect(reverse('cart'))

    return render(request, 'store/checkout.html', context)

@login_required(login_url='login')
def processOrder(request):
    data = json.loads(request.body)
    customer = request.user.customer
    order = Order.objects.get(customer=customer, complete=False)
    items = order.cart_set.all()
    if request.method == 'POST':
        # transaction_id = datetime.now().timestamp()
        if order.get_cart_total != int(data['total']) and data['ok'] == False:
            messages.warning(request, 'يوجد خطأ ما.. يرجى إعادة المحاولة مرة آخرى.')
            return JsonResponse("False", safe=False)
  
        if order.get_cart_total == int(data['total']) and data['ok'] == True:
            order.complete = True
            order.total = order.get_cart_total
            order.date_orderd = timezone.now()
            res = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(10))
            order.code = str(res)
            if order.coupon:
                order.coupon_discount = order.coupon.discount

            order.save()

            for i in items:

                if i.product.is_discount:
                    product_price = i.product.is_discount
                else:
                    product_price = i.product.price

                myDoneOrder = OrderDone.objects.create(order=order, product=i.product.name, product_price=product_price, color=i.color, size=i.size, quantity=i.quantity)
                myDoneOrder.save()
            
            Cart.objects.filter(order=order).delete()
            superusers = User.objects.filter(is_superuser=True)
            payload = {"head": "SistersStore", "body": f" قام المستخدم {order.customer} بطلب طلب جديد. "}
            send_user_notification(user=superusers[0], payload=payload, ttl=1000)
            
            messages.success(request, 'تمت عمليت الشحن بنجاح... يمكنك الآن رؤية الطلبات الخاصة بك.')
            return JsonResponse("True", safe=False)

    return JsonResponse("Payment Complate", safe=False)

@login_required(login_url='login')
@require_POST
def coupon_apply(request):
    now = timezone.now()
    if not request.POST.get('coupon'):
        messages.warning(request, 'الرجاء إدخال الكوبون لتفعيله.')
        return HttpResponseRedirect(reverse('cart'))
    else:
        code = request.POST.get('coupon')
        try:
            coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True)
            customer = request.user.customer
            order = Order.objects.get(customer=customer, complete=False)
            if order.coupon == coupon:
                messages.info(request, 'تم إستخدام هذا الكوبون بالفعل.')
                return HttpResponseRedirect(reverse('cart'))

            order.coupon = coupon
            order.coupon_discount = coupon.discount
            order.save()
            messages.success(request, f'شكرا لك... تم تفعيل الكوبون "{coupon.code}" بنجاح.')
        except Coupon.DoesNotExist:
            messages.warning(request, 'هذا الكوبون غير فعال.')
        return HttpResponseRedirect(reverse('cart'))

@login_required(login_url='login')
def add_favorite(request, pk):
    customer = request.user.customer
    product = Product.objects.get(pk=pk)
    favorite = Favorite.objects.filter(customer=customer, product=product)
    
    if favorite.exists():
        favorite[0].product.remove(product)
        messages.success(request, 'تمت الإزالة المنتج من المفضلة بنجاح.')
    else:
        favorite = Favorite.objects.get(customer=customer)
        favorite.product.add(product)
        messages.success(request, 'تمت الإضافة المنتج للمفضلة بنجاح.')
    
    return HttpResponseRedirect(reverse('product_detail', args=[pk]))
    
@login_required(login_url='login')
def favorite(request):
    customer = request.user.customer
    favorite = Favorite.objects.get(customer=customer)
    products = favorite.product.all()
    
    # paginator
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_page)

    context = {
        'products': products,
        'cart_items': cart_items(request),
        'favorite_number': favorite_number(request),
    }

    return render(request, 'store/favorite.html', context)




