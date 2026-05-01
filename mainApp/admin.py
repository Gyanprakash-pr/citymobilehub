from django.contrib import admin
from .models import *

class ProductAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/admin_product.js',)

admin.site.register((
    Maincategory,
    Subcategory,
    Brand,
    Seller,
    Buyer,
    Wishlist,
    Checkout,
    CheckoutProducts,
    Newslatter,
    Contact,
    Coupon,
    StoreInfo,
    ChatSession,
    ChatMessage,
    Review,
    Reply
))
admin.site.register(Product, ProductAdmin)
