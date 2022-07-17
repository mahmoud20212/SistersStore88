from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm, UserUpdateForm, UserChangePasswordForm, CustomerUpdateForm
from .models import Customer, Country, City
from store.models import Order, Favorite

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
    countries = Country.objects.all()
    cities = City.objects.all()
    u_form = UserUpdateForm(instance=request.user)
    c_form = CustomerUpdateForm(instance=customer)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        c_form = CustomerUpdateForm(request.POST, instance=customer)

        if u_form.is_valid() and c_form.is_valid():
            data = c_form.save(commit=False)
            if c_form.cleaned_data['city']: 
                if c_form.cleaned_data['country']:
                    city = City.objects.get(city=c_form.cleaned_data['city'])
                    country = Country.objects.get(country=c_form.cleaned_data['country'])
                    if city.country == country:
                        data.city = city
                    else:
                        messages.warning(request, 'هذه المدينة ليست ضمن هذه الدولة.')
                        return HttpResponseRedirect(reverse('profile'))
                else:
                    messages.warning(request, 'الرجاء تحديد الدولة أولا.')
                    return HttpResponseRedirect(reverse('profile'))
            
            data.save()
            u_form.save()
            messages.success(request, 'تم تحديث الملف الشخصي.')
            return HttpResponseRedirect(reverse('profile'))      
        
    context = {
        'u_form': u_form,
        'c_form': c_form,
        'cart_items': cart_items(request),
        'favorite_number': favorite_number(request),
        'orders': orders,
        'countries': countries,
        'cities': cities,
    }
    return render(request, 'user/profile.html', context)

@login_required(login_url='login')
def user_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user.customer == order.customer:
        context = {
            'order': order,
        }
        return render(request, 'user/order.html', context)
    else:
        return HttpResponseForbidden()

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

