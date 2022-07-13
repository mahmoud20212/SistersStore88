from django import template
from store.models import Product

register = template.Library()
@register.inclusion_tag('store/random_product.html')
def rand():
    context = {
        'r_product': Product.objects.all().order_by('?')[:8]
    }
    return context