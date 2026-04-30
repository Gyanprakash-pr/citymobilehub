# Template tags for product related functionality
from django import template
register = template.Library()
from mainApp.models import CheckoutProducts
from mainApp.models import Checkout

@register.filter("checkColor")
def checkColor(color, item):
    flag = False
    for i in color.split(","):
        if(i==item):
            flag=True
            break
    return flag

@register.filter("orderStatus")
def orderStatus(request,num):
    if(num==0):
        return "Cancelled"
    elif(num==1):
        return "Not Packed"
    elif(num==2):
        return "Packed"
    elif(num==3):
        return "Out for Delivery"
    else:
        return "Delivered"

@register.filter("paymentStatus")
def paymentStatus(request,num):
    if(num==1):
        return "Pending"
    else:
        return "Done"

@register.filter("paymentStatusCon")
def paymentStatusCon(request,num):
    if(num==1):
        return True
    else:
        return False

@register.filter("orderItem")
def orderItem(request,num):
    check = Checkout.objects.get(id=num)
    p = CheckoutProducts.objects.filter(checkout=check)
    return p
   



from mainApp.models import Product
@register.filter("categoryImage")
def categoryImage(cat):
    try:
        p = Product.objects.filter(maincategory=cat).first()
        if p and p.pic1:
            return p.pic1.url
    except Exception:
        pass
    return ""
@register.filter("split")
def split(value, arg):
    return value.split(arg)

from mainApp.models import Seller
@register.filter("is_seller")
def is_seller(user):
    if user.is_authenticated:
        return Seller.objects.filter(username=user.username).exists()
    return False
