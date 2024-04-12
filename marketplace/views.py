
from vendor.models import Vendor
from menu.models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from .models import Cart, Tax
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from vendor.models import OpeningHour
from orders.forms import OrderForm
from accounts.models import userProfile


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
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    #Check Current Days's opening hours
    today_date = date.today()
    today = today_date.isoweekday()

    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

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
    now = datetime.now()
    print(now)
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'need_login': need_login,
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
            return redirect(request.META.get('HTTP_REFERER', '/'))
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


@login_required(login_url='login')
def cart(request):
    cart_items = None
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).order_by('created_at')

    subtotal = 0
    tax = 0
    tax_dict = {}

    for item in cart_items:
        subtotal += item.fooditem.price * item.quantity
    
    get_tax = Tax.objects.filter(is_active=True)
    for tax in get_tax:
        tax_type = tax.tax_type
        tax_percentage = tax.tax_percentage
        tax_amount = round((tax_percentage * subtotal) / 100, 2)
        tax_dict[tax_type] = {tax_percentage: tax_amount}

    total = subtotal + sum(sum(tax_dict[tax_type].values()) for tax_type in tax_dict.keys())

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'tax_dict': tax_dict,
    }
    return render(request, 'marketplace/cart.html', context)


def search(request):
    return HttpResponse('search page')

@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    user_profile = userProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        # 'address': request.user.address,
        # 'country': request.user.country,
        # 'state': request.user.state,
        # 'city': request.user.city,
        # 'pin_code': request.user.pin_code, 
    }

    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)