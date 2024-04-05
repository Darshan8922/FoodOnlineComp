
from vendor.models import Vendor
from menu.models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from .models import Cart
# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)



def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    cart_items = None
    need_login = False
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).select_related('fooditem')
        cart_item_dict = {cart_item.fooditem.id: cart_item.quantity for cart_item in cart_items}
    else:
        need_login = True

    for category in categories:
        for fooditem in category.fooditems.all():
            if cart_items:
                fooditem.quantity_in_cart = cart_item_dict.get(fooditem.id, 0)
            else:
                # If user is not logged in, set quantity_in_cart to 0 for all items
                fooditem.quantity_in_cart = 0

    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'need_login': need_login
    }
    return render(request, 'marketplace/vendor_detail.html', context)

# def add_to_cart(request, food_id):
#     if request.user.is_authenticated:
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
#             try:
#                 fooditem = FoodItem.objects.get(id = food_id)

#                 try:
#                     chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
#                     chkCart.quantity += 1
#                     chkCart.save()
#                     return JsonResponse({'status': 'Success'})
#                 except:
#                     chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
#                     return JsonResponse({'status': 'Success'})
#             except:
#                 return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
#         else:
#             return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
        
#     else:
#         return JsonResponse({'status': 'Failed', 'message': 'Please login to continue'})
# def add_to_cart(request, food_id=None):
#     if request.user.is_authenticated:
#         fooditem = get_object_or_404(FoodItem, id=food_id)
#         try:
#             chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
#             chkCart.quantity += 1
#             chkCart.save()
#         except Cart.DoesNotExist:
#             Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
#         vendor_slug = fooditem.vendor.vendor_slug
#         return redirect('vendor_detail', vendor_slug=vendor_slug)
#     else:
#         print("Invalid")

def add_to_cart(request, food_id=None):
    if request.user.is_authenticated:
        fooditem = FoodItem.objects.get(id = food_id)
        try:
            chkCart = Cart.objects.get(user= request.user, fooditem=fooditem)
            chkCart.quantity+=1
            chkCart.save()
            vendor_slug = fooditem.vendor.vendor_slug
        # Redirect to the vendor_detail view with the appropriate vendor_slug
            return redirect('vendor_detail', vendor_slug=vendor_slug)
        except:
            chkCart = Cart.objects.create(user= request.user, fooditem=fooditem, quantity=1)
            vendor_slug = fooditem.vendor.vendor_slug
        # Redirect to the vendor_detail view with the appropriate vendor_slug
            return redirect('vendor_detail', vendor_slug=vendor_slug)
    else:
        return redirect('login')


def decrease_cart(request, food_id = None):
    if request.user.is_authenticated:
        fooditem = get_object_or_404(FoodItem, id=food_id)
        try:
            cart_item = Cart.objects.get(user=request.user, fooditem=fooditem)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()  # Remove from cart if quantity becomes 0
            vendor_slug = fooditem.vendor.vendor_slug
            return redirect(request.META.get('HTTP_REFERER', '/'))
        except Cart.DoesNotExist:
            pass  # No action needed if item is not in the cart
    return redirect(request.META.get('HTTP_REFERER', '/'))

def cart(request):
    cart_items = None
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).select_related('fooditem')
    context = {
        'cart_items': cart_items
    }
    return render(request, 'marketplace/cart.html', context)