from django.shortcuts import render, redirect
from vendor.models import Vendor
from menu.models import *
from django.shortcuts import get_object_or_404
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
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items' : cart_items
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
        print("Invalid")
        #if request.is_ajax():
    #     if request.headers.get('x-requested-with') == 'XMLHttpRequest':    
    #         try:
    #             fooditem = FoodItem.objects.get(id = food_id)

    #             try:
    #                 chkCart = Cart.objects.get(user= request.user, fooditem=fooditem)
    #                 chkCart.quantity+=1
    #                 chkCart.save()
    #                 return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity', 'cart_counter':get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
    #             except:
    #                 chkCart = Cart.objects.create(user= request.user, fooditem=fooditem, quantity=1)
    #                 return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart', 'cart_counter':get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
    #         except:
    #             return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
    #     else:
    #         return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
        
    # else:
    #     return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})   



