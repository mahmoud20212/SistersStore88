from .models import Category, Tag

def categories(request):
    return {'my_categories': Category.objects.all()[:4]}

def tags(request):
    return {'tags': Tag.objects.all()}
        