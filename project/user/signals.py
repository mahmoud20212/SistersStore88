from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Customer
from store.models import Favorite, Order
from webpush import send_user_notification


@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        customer = Customer.objects.create(user=instance)
        favorite = Favorite.objects.create(customer=customer)
        
@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    instance.customer.save()

@receiver(post_save, sender=Order)
def change_status_for_order(sender, instance, created, **kwargs):
    if instance:
        if instance.complete:
            user = User.objects.get(customer=instance.customer)
            if instance.status == 'under construction':
                payload = {"head": "SistersStore", "body": "تم تحديث حالة الطلب لديك الى قيد الإنشاء"}
                send_user_notification(user=user, payload=payload, ttl=1000)
            elif instance.status == 'in store':
                payload = {"head": "SistersStore", "body": "تم تحديث حالة الطلب لديك الى في المخزن"}
                send_user_notification(user=user, payload=payload, ttl=1000)
            elif instance.status == 'in the way':
                payload = {"head": "SistersStore", "body": "تم تحديث حالة الطلب لديك الى في الطريق"}
                send_user_notification(user=user, payload=payload, ttl=1000)
            elif instance.status == 'delivered':
                payload = {"head": "SistersStore", "body": "تم تحديث حالة الطلب لديك الى تم الإستلام"}
                send_user_notification(user=user, payload=payload, ttl=1000)
        
    
    
    