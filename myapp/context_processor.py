from .models import category , CartItems , Cart ,Product
from myapp.views import _cart_id
from django.db.models import Count
#from django.core.exceptions import DoesNotExist

def menu_links(request):
    links = category.objects.all()
    return dict(links=links)





def menu_links(request):
    # Get all categories with their respective product counts
    categories_with_count = category.objects.annotate(product_count=Count('product'))
    return {'lcount': categories_with_count}



# def counter(request):
#     cart_count = 0
#     if 'admin' in request.path:
#         return {}
#     else:
#         try:
#             cart = Cart.objects.filter(cart_id=_cart_id(request))
#             if request.user.is_authenticated:
#                 cart_items = CartItems.objects.all().filter(user=request.user)
#             else:
#                 cart_items = CartItems.objects.all().filter(cart=cart[:1])
#             for cart_item in cart_items:
#                 cart_count += cart_item.quantity
#         except Cart.DoesNotExist:
#             cart_count = 0
#     return dict(cart_count=cart_count)

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItems.objects.all().filter(user=request.user)
                cart_count = cart_items.count()
            else:
                cart_items = CartItems.objects.all().filter(cart=cart[:1])
                cart_count = cart_items.count()
            # cart_item = CartItems.objects.all().filter(cart=cart[:1])
            # cart_count = cart_item.count()
            # for item in cart_item:
            #     cart_count += item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)
