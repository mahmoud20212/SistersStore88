from django.contrib import admin
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    model = Customer
    list_display = ['user', 'phone_number', 'location']

admin.site.register(Customer, CustomerAdmin)


