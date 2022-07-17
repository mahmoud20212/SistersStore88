from django.contrib import admin
from .models import *
# from .forms import RequiredInlineFormSet

class PhotoInLine(admin.TabularInline):
    # formset = RequiredInlineFormSet
    model = ProductPhoto
    extra = 1
    min_num = 1

class OrderDoneInLine(admin.TabularInline):
    model = OrderDone
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','price', 'status', 'discount', 'category', 'date_created')
    inlines = [PhotoInLine,]

class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'full_name', 'location', 'phone_number', 'payment_method', 'orderd_date', 'status', 'code', 'coupon', 'total', 'complete', 'done')
    list_filter = ('complete','done')
    inlines = [OrderDoneInLine,]
    search_fields = ('code',)
    exclude = ('complete',)

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code','valid_from', 'valid_to', 'discount', 'active',)
    list_filter = ('active', 'valid_from', 'valid_to',)
    search_fields = ('code',)


admin.site.register(Contact)
admin.site.register(Cart)
admin.site.register(Favorite)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Size)
admin.site.register(Color)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(FAQ)

