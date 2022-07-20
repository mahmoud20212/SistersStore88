import string  
import secrets # import package 
from django.db import models
from django.utils import timezone
from user.models import Customer
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField

# Create your models here.

class Contact(models.Model):
    email = models.EmailField()
    description = models.TextField()

    def __str__(self):
        return self.email

class FAQ(models.Model):
    title = models.CharField(max_length=150)
    description = RichTextField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']

class Color(models.Model):
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.color

class Size(models.Model):
    size = models.CharField(max_length=50)

    class Meta:
        ordering = ['size']

    def __str__(self):
        return self.size

    def save(self, *args, **kwargs):
        self.size = self.size.upper()
        return super().save(*args, **kwargs)
        
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    tag = models.CharField(max_length=50)

    def __str__(self):
        return self.tag

class Product(models.Model):
    CHOOSE = (
        ('New','New'),
        ('Sale','Sale'),
        ('Ended','Ended'),
    )
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to ='photos/', blank=False)
    status = models.CharField(max_length=50, choices=CHOOSE, blank=True, null=True)
    # size = models.ManyToManyField(Size)
    # color = models.ManyToManyField(Color)
    # available_number = models.IntegerField(validators=[MinValueValidator(0)], null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    description = RichTextField()
    tags = models.ManyToManyField(Tag)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-id']
    
    def __str__(self):
        return self.name

    @property
    def is_discount(self):
        if self.discount:
            return int(self.price - (self.price * (self.discount / 100)))
        else:
            return False

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    size = models.ManyToManyField(Size)
    # available_number = models.IntegerField(validators=[MinValueValidator(0)], null=True)

class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='photos') # product.photos.all مثال  <model>_set.all بدل  related_name يستخدم 
    image = models.ImageField(upload_to ='photos/', blank=False, null=False)

    def __str__(self):
        return self.product.name

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField()

    def __str__(self):
        return self.code


class Order(models.Model):
    STATUSES = (
        ('under construction','under construction'),
        ('in store','in store'),
        ('in the way','in the way'),
        ('delivered','delivered'),
    )
    METHOD = (
        ('paypal','paypal'),
        ('credit card','credit card'),
        ('paiement when recieving','paiement when recieving'),
    )
    code = models.CharField(blank=True, null=True, max_length=10)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    created_in = models.DateTimeField(default=timezone.now)
    orderd_date = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, choices=METHOD, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUSES, default=STATUSES[0][0], blank=True, null=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
    total = models.IntegerField(default=0, validators=[MinValueValidator(0)], null=True, blank=True)
    coupon_discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    done = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.customer}'

    def full_name(self):
        return f'{self.customer.user.first_name} {self.customer.user.last_name}'

    def location(self):
        return f'{self.customer.location}'

    def phone_number(self):
        return f'{self.customer.phone_number}'

    def save(self, *args, **kwargs):
        res = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(10))
        self.code = str(res)
        return super().save(*args, **kwargs)
    
    @property
    def get_cart_total(self):
        cart_items = self.cart_set.all()
        total = sum([item.get_total for item in cart_items])
        
        if self.coupon and self.coupon.discount:
            if self.coupon.active:
                total = int(total - (total * (self.coupon.discount / 100)))
            
        return total
    
    @property
    def discount_amount(self):
        if self.coupon and self.coupon.discount:
            if self.coupon.active:
                cart_items = self.cart_set.all()
                total = sum([item.get_total for item in cart_items])
                discount_amount = int(total * (self.coupon.discount / 100))
                return discount_amount
            else:
                return 0

    @property
    def get_cart_items(self):
        orderitems = self.cart_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    color = models.CharField(max_length=50, null=True)
    size = models.CharField(max_length=50, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    @property
    def get_total(self):
        if self.product.is_discount:
            total = self.product.is_discount * self.quantity
        else:
            total = self.product.price * self.quantity
        return total

class OrderDone(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    product = models.CharField(max_length=50, null=True)
    product_price = models.PositiveIntegerField(null=True)
    color = models.CharField(max_length=50, null=True)
    size = models.CharField(max_length=50, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    total = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

class Favorite(models.Model):
    product = models.ManyToManyField(Product, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)

class Comment(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    description = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f'علق {self.name} على {self.product}'

    class Meta:
        ordering = ['-comment_date']
