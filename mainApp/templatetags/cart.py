from django import template
from mainApp.models import Product
register = template.Library()

@register.filter("cartColor")
def cartColor(request, num):
    cart = request.session.get("cart",None)
    if(cart):
        return cart[num][2]
    else:
        return ""

@register.filter("cartSize")
def cartSize(request, num):
    cart = request.session.get("cart",None)
    if(cart):
        return cart[num][3]
    else:
        return ""

@register.filter("cartQty")
def cartQty(request, num):
    cart = request.session.get("cart",None)
    if(cart):
        return cart[num][1]
    else:
        return ""

@register.filter("cartTotal")
def cartTotal(request, num):
    cart = request.session.get("cart",None)
    if(cart):
        p = Product.objects.get(id=int(cart[num][0]))
        return cart[num][1]*p.finalprice
    else:
        return ""

@register.filter("cartProductName")
def cartProductName(request, num):
    cart = request.session.get("cart",None)
    if(cart):
        p = Product.objects.get(id=int(cart[num][0]))
        return p.name
    else:
        return ""

@register.filter("cartProductPrice")
def cartProductPrice(request, num):
    cart = request.session.get("cart",None)
    if(cart):
        p = Product.objects.get(id=int(cart[num][0]))
        return p.finalprice
    else:
        return ""

@register.filter("cartProductImage")
def cartProductImage(request, num):
    cart = request.session.get("cart",None)
    if(cart):
        p = Product.objects.get(id=int(cart[num][0]))
        return p.pic1.url
    else:
        return ""



@register.filter
def multiply(value, arg):
    return value * arg