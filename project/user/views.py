from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm, UserUpdateForm, UserChangePasswordForm
from .models import Customer
from store.models import Order, OrderDone, Favorite

# ============================================

def cart_items(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        return order.get_cart_items

def favorite_number(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        try:
            favorite = Favorite.objects.get(customer=customer)
            product = favorite.product.all().count()
            return product
        except Favorite.DoesNotExist:
            customer = request.user.customer
            favorite = Favorite.objects.create(customer=customer)
            favorite.save()
    return 0

# ============================================

def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password1'])
            new_user.save()
            messages.success(request, f'شكرا {new_user}... تم انشاء الحساب بنجاح يمكنك الآن تسجيل الدخول.')
            return HttpResponseRedirect(reverse('login'))
    else:  
        form = UserCreationForm()

    context = {
        'form': form,
    }
    return render(request, 'user/register.html', context)

def userLogin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.warning(request, 'الرجاء إدخال إسم المستخدم وكلمة المرور.')
        else:
            user = authenticate(request, username=username, password=password)
            if user != None:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                messages.warning(request, 'هناك خطأ في إسم المستخدم أو كلمة المرور.')

    return render(request, 'user/login.html')

def userLogout(request):
    messages.success(request, 'تم تسجيل خروجك بنجاح.')
    logout(request)
    return HttpResponseRedirect(reverse('login'))

@login_required(login_url='login')
def userProfile (request):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer, complete=True)
    all_order = []
    for order in orders:
        order_done = OrderDone.objects.filter(order=order)
        all_order.append(order_done)

    if request.method == 'POST':
        customer = Customer.objects.get(id=request.user.id)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        
        customer.phone_number = request.POST.get('phone_number')
        customer.location = request.POST.get('location')

        if u_form.is_valid():
            u_form.save()
            customer.save()
            messages.success(request, 'تم تحديث الملف الشخصي.')
            return HttpResponseRedirect(reverse('profile'))    
    else:
        u_form = UserUpdateForm(instance=request.user)
        
    context = {
        'u_form': u_form,
        'order_done': all_order,
        'cart_items': cart_items(request),
        'favorite_number': favorite_number(request),
    }
    return render(request, 'user/profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = UserChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'تم تغير كلمة المرور الخاصة بك.')
            return HttpResponseRedirect(reverse('profile'))
        else:
            messages.warning(request, 'الرجاء تصحيح الخطأ أدناه.')
    else:
        form = UserChangePasswordForm(request.user)

    context = {
        'form': form,
        'cart_items': cart_items(request),
        'favorite_number': favorite_number(request),
    }

    return render(request, 'user/password/change_password.html', context)

