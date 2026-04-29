import json
from django.http import JsonResponse
from django.shortcuts import redirect, render,HttpResponseRedirect
from django.contrib import messages,auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.urls import reverse
import os
import json
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import *
from django.db import transaction

def seed_store(request):
    """Public reset view for Desi Mobile transformation"""
    with transaction.atomic():
        # 1. Clear ABSOLUTELY EVERYTHING (Users, Products, Categories)
        User.objects.all().delete()
        Product.objects.all().delete()
        Maincategory.objects.all().delete()
        Subcategory.objects.all().delete()
        Brand.objects.all().delete()
        Buyer.objects.all().delete()
        Checkout.objects.all().delete()
        Newslatter.objects.all().delete()
        Contact.objects.all().delete()
        
        # 2. Create fresh superuser for YOU
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        
        # 3. Add Real Mobile Categories
        mc_names = ["Smartphones", "Chargers & Cables", "Cases & Covers", "Audio & Gadgets", "Screen Protection", "Power Banks"]
        for name in mc_names:
            Maincategory.objects.get_or_create(name=name)
            
        # 3. Add Real Mobile Brands
        brand_names = ["Apple", "Samsung", "OnePlus", "Xiaomi", "Realme", "Vivo", "Oppo", "Nothing", "boAt", "Noise", "JBL"]
        for name in brand_names:
            Brand.objects.get_or_create(name=name)
            
        # 4. Add Subcategories
        sc_names = ["iPhone Cases", "Samsung Covers", "Type-C Cables", "Wall Chargers", "TWS Earbuds", "Fast Chargers", "Neckbands"]
        for name in sc_names:
            Subcategory.objects.get_or_create(name=name)
            
    return JsonResponse({"status": "success", "message": "Store Reset Complete! All Fashion data wiped. Welcome to Desi Mobile."})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import ChatSession, ChatMessage
import json
import uuid
from datetime import datetime
import razorpay 
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from .models import Buyer, Checkout  # Import your models here
from django.conf import settings
from OnlineBazar.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY
client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))



from .models import *


def Homepage(request):
    products = Product.objects.all()
    products=products.order_by('-id')[:8]  # Show latest 8
    maincategory = Maincategory.objects.all()
    if(request.method=='POST'):
        try:
            email = request.POST.get("email")
            n = Newslatter()
            n.email=email
            n.save()
        except:
            pass
        return HttpResponseRedirect("/")
    return render(request,"index.html",{"Product":products, "Maincategory": maincategory})

def ShopPage(request,mc,sc,br):
    
    maincategory = Maincategory.objects.all()
    subcategory = Subcategory.objects.all()
    brand = Brand.objects.all()
    if(request.method=="POST"):
        search = request.POST.get('search')
        products = Product.objects.filter(Q(name__icontains=search))
    else:
        if(mc=="All" and sc=="All" and br=="All"):
            products = Product.objects.all()
        elif(mc!="All" and sc=="All" and br=="All"):
            cat = Maincategory.objects.filter(name__iexact=mc).first()
            if cat:
                products = Product.objects.filter(maincategory=cat)
            else:
                products = Product.objects.all()
        elif(mc=="All" and sc!="All" and br=="All"):
            cat = Subcategory.objects.filter(name__iexact=sc).first()
            if cat:
                products = Product.objects.filter(subcategory=cat)
            else:
                products = Product.objects.all()
        elif(mc=="All" and sc=="All" and br!="All"):
            brand_obj = Brand.objects.filter(name__iexact=br).first()
            if brand_obj:
                products = Product.objects.filter(brand=brand_obj)
            else:
                products = Product.objects.all()
        elif(mc!="All" and sc!="All" and br=="All"):
            m_cat = Maincategory.objects.filter(name__iexact=mc).first()
            s_cat = Subcategory.objects.filter(name__iexact=sc).first()
            if m_cat and s_cat:
                products = Product.objects.filter(maincategory=m_cat,subcategory=s_cat)
            else:
                products = Product.objects.all()
        elif(mc!="All" and sc=="All" and br!="All"):
            m_cat = Maincategory.objects.filter(name__iexact=mc).first()
            b_obj = Brand.objects.filter(name__iexact=br).first()
            if m_cat and b_obj:
                products = Product.objects.filter(maincategory=m_cat,brand=b_obj)
            else:
                products = Product.objects.all()
        elif(mc=="All" and sc!="All" and br!="All"):
            s_cat = Subcategory.objects.filter(name__iexact=sc).first()
            b_obj = Brand.objects.filter(name__iexact=br).first()
            if s_cat and b_obj:
                products = Product.objects.filter(subcategory=s_cat,brand=b_obj)
            else:
                products = Product.objects.all()
        elif(mc!="All" and sc!="All" and br!="All"):
            m_cat = Maincategory.objects.filter(name__iexact=mc).first()
            s_cat = Subcategory.objects.filter(name__iexact=sc).first()
            b_obj = Brand.objects.filter(name__iexact=br).first()
            if m_cat and s_cat and b_obj:
                products = Product.objects.filter(maincategory=m_cat,subcategory=s_cat,brand=b_obj)
            else:
                products = Product.objects.all()
            
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    sort_by = request.GET.get('sort', 'featured')

    if isinstance(products, list):
        pass # If it was somehow converted to list elsewhere, though it shouldn't be
    else:
        # Apply Price Filter
        if min_price:
            try: 
                products = products.filter(finalprice__gte=int(min_price))
            except ValueError:
                min_price = None
        if max_price:
            try: 
                products = products.filter(finalprice__lte=int(max_price))
            except ValueError:
                max_price = None
            
        # Apply Sorting
        if sort_by == 'price-low':
            products = products.order_by('finalprice')
        elif sort_by == 'price-high':
            products = products.order_by('-finalprice')
        elif sort_by == 'newest':
            products = products.order_by('-id')
        elif sort_by == 'bestselling':
            products = products.order_by('-id')
        else:
            # Default sorting: newest first (replaces the old [::-1])
            products = products.order_by('-id')

    # Build counts for sidebar filters
    from django.db.models import Count
    maincategory_with_counts = maincategory.annotate(product_count=Count('product'))
    brand_with_counts = brand.annotate(product_count=Count('product'))
    total_products = Product.objects.count()

    return render(request,"shop.html",{"Product":products,
                                      "Maincategory":maincategory_with_counts,
                                      "Subcategory":subcategory,
                                      "Brand":brand_with_counts,
                                      "mc":mc,"sc":sc,"br":br,
                                      "min_price": min_price,
                                      "max_price": max_price,
                                      "sort_by": sort_by,
                                      "total_products": total_products,
                                      })
    
def Login(request):
    if(request.method=='POST'):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(username=username,password=password)
        if(user is not None):
            auth.login(request,user)
            if(user.is_superuser):
                return HttpResponseRedirect("/admin/")
            else:
                return HttpResponseRedirect("/profile/")
        else:
            messages.error(request,"Invalid Username or Password")
    return render(request,"login.html")


def ForgetPassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        new_password = request.POST.get("password1")
        confirm_password = request.POST.get("password2")

        # Check if passwords match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "forgetpws.html")

        try:
            # Check if user exists with the given email
            user = User.objects.get(email=email)
            
            # Set the new password
            user.set_password(new_password)
            user.save()

            # Notify user about the success
            messages.success(request, "Password reset successful! You can now log in.")
            
            # Redirect to login page
            return redirect(reverse('login'))

        except User.DoesNotExist:
            # If the email is not found in the database
            messages.error(request, "Email not found! Please enter a registered email.")

    return render(request, "forgetpws.html")

def SignUp(request):
    if(request.method=="POST"):
        actype = request.POST.get('actype')
        if(actype=="seller"):
            u = Seller()
        else:
            u = Buyer()
        u.name = request.POST.get("name")
        u.username = request.POST.get("username")
        u.phone = request.POST.get("phone")
        u.email = request.POST.get("email")
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")  
        if(password==cpassword):
            try:
                user = User.objects.create_user(username=u.username,password=password,email=u.email)
                user.save()
                u.save()
                return HttpResponseRedirect("/login/")
            except:
                messages.error(request,"User Name Already Taken !!!!")   

                return render(request,"Sgnup.html")


        else:
             messages.error(request,"Password And Confirm Password does not Matched !!!!")   

    return render(request,"Sgnup.html")

@login_required(login_url='/login/')
def ProfilePage(request):

    user = User.objects.get(username=request.user)
    if(user.is_superuser):
        return HttpResponseRedirect("/admin/")
    else:
        try:

            seller = Seller.objects.get(username=request.user)
            products = Product.objects.filter(seller=seller)
            products = products[::-1]
            
            # Seller Stats
            from mainApp.models import CheckoutProducts
            seller_orders = CheckoutProducts.objects.filter(seller=seller).order_by('-id')
            total_sales = seller_orders.count()
            total_revenue = sum(item.total for item in seller_orders)
            
            context = {
                "User": seller,
                "products": products,
                "total_sales": total_sales,
                "total_revenue": total_revenue,
                "seller_orders": seller_orders
            }
            return render(request,"sellerprofile.html", context)
        except:
            
            buyer = Buyer.objects.get(username=request.user)
            wishlist = Wishlist.objects.filter(buyer=buyer)
            checkouts = Checkout.objects.filter(buyer=buyer)
            checkouts = checkouts[::-1]
            
            return render(request,"buyerprofile.html",{"User":buyer,"Wishlist":wishlist,"Orders":checkouts})

@login_required(login_url='/login/')
def updateProfilePage(request):
    user = User.objects.get(username=request.user)
    if(user.is_superuser):
        return HttpResponseRedirect("/admin/")
    else:
        try:
            user = Seller.objects.get(username=request.user)
        except:
            user = Buyer.objects.get(username=request.user)
        if(request.method=="POST"):


            user.name=request.POST.get('name')
            
            user.email=request.POST.get('email')
            user.phone=request.POST.get('phone')
            user.addressline1=request.POST.get('addressline1')
            user.pin=request.POST.get('pin')
            user.city=request.POST.get('city')
            user.state=request.POST.get('state')
       
            if request.FILES.get("pic"):
                if user.pic:
                    pic_path = os.path.join("media", str(user.pic))
                    if os.path.exists(pic_path):
                        os.remove(pic_path)
                user.pic = request.FILES.get('pic')
                
                user.save()
                        
         
            # if(request.FILES.get("pic")):
            #     if(user.pic):
            #         os.remove("media/"+str(user.pic))
            #     user.pic=request.FILES.get('pic')
            # user.save()
            return HttpResponseRedirect("/profile/")
    return render(request,"updateProfile.html",{"User":user}) 
  
@login_required(login_url='/login/')    
def addproduct(request):
    # Security: Only allow registered Sellers to access this page
    try:
        seller_profile = Seller.objects.get(username=request.user.username)
    except Seller.DoesNotExist:
        messages.error(request, "Only registered sellers can add products.")
        return HttpResponseRedirect("/profile/")

    maincategory = Maincategory.objects.all()
    subcategory = Subcategory.objects.all()
    brand = Brand.objects.all()
    if(request.method=="POST"):
        p = Product()
        p.name = request.POST.get('name')
        p.maincategory = Maincategory.objects.get(name=request.POST.get('maincategory'))

        p.subcategory = Subcategory.objects.get(name=request.POST.get('subcategory'))
        p.brand = Brand.objects.get(name=request.POST.get('brand'))
        p.baseprice = int(request.POST.get('baseprice'))
        p.discount = int(request.POST.get('discount'))
        p.finalprice = p.baseprice-p.baseprice*p.discount/100
        color=""
        if(request.POST.get("Red")):
            color=color+"Red,"
        if(request.POST.get("Green")):
            color=color+"Green,"
        if(request.POST.get("Yellow")):
            color=color+"Yellow,"
        if(request.POST.get("Pink")):
            color=color+"Pink,"
        if(request.POST.get("White")):
            color=color+"White,"
        if(request.POST.get("Black")):
            color=color+"Black,"
        if(request.POST.get("Blue")):
            color=color+"Blue,"
        if(request.POST.get("Brown")):
            color=color+"Brown,"
        if(request.POST.get("SkyBlue")):
            color=color+"SkyBlue,"
        if(request.POST.get("Orange")):
            color=color+"Orange,"
        if(request.POST.get("Navy")):
            color=color+"Navy,"
        if(request.POST.get("Gray")):
            color=color+"Gray,"
        p.color=color




        p.description = request.POST.get('description')
        p.stock = request.POST.get('stock')
        p.pic1 = request.FILES.get('pic1')
        p.pic2 = request.FILES.get('pic2')
        p.pic3 = request.FILES.get('pic3')
        p.pic4 = request.FILES.get('pic4')
        try:
            p.seller = Seller.objects.get(username=request.user.username)
        except:
            return HttpResponseRedirect("/profile/")
        p.save()
        return HttpResponseRedirect("/profile/")                    
    
    return render(request,"addProduct.html",{"Maincategory":maincategory,"Subcategory":subcategory,"Brand":brand})


@login_required(login_url='/login/')
def deleteproduct(request,num):
    try:
        p = Product.objects.get(id=num)
        seller = Seller.objects.get(username=request.user)
        if(p.seller==seller):
            p.delete()
        return HttpResponseRedirect("/profile/")
    except:
        return HttpResponseRedirect("/profile/")
    



    
@login_required(login_url='/login/')
def Editproduct(request, num):
    try:
        product = Product.objects.get(id=num)
        seller = Seller.objects.get(username=request.user)
        
        if product.seller != seller:
            return HttpResponseRedirect("/profile/")

        # Get all available options excluding current selections
        maincategories = Maincategory.objects.exclude(name=product.maincategory)
        subcategories = Subcategory.objects.exclude(name=product.subcategory)
        brands = Brand.objects.exclude(name=product.brand)

        if request.method == "POST":
            # Process form data
            product.name = request.POST.get('name')
            
            try:
                product.maincategory = Maincategory.objects.get(name=request.POST.get('maincategory'))
                product.subcategory = Subcategory.objects.get(name=request.POST.get('subcategory'))
                product.brand = Brand.objects.get(name=request.POST.get('brand'))
            except (Maincategory.DoesNotExist, Subcategory.DoesNotExist, Brand.DoesNotExist):
                return HttpResponseRedirect("/profile/")

            # Process pricing
            try:
                product.baseprice = int(request.POST.get('baseprice', 0))
                product.discount = int(request.POST.get('discount', 0))
                product.finalprice = product.baseprice - (product.baseprice * product.discount / 100)
            except (ValueError, TypeError):
                return HttpResponseRedirect("/profile/")

            # Process colors
            available_colors = ['Red', 'Green', 'Yellow', 'Pink', 'White', 'Black', 
                              'Blue', 'Brown', 'SkyBlue', 'Orange', 'Navy', 'Gray']
            selected_colors = [color for color in available_colors if request.POST.get(color)]
            product.color = ",".join(selected_colors) + "," if selected_colors else ""

            # Process description and stock
            product.description = request.POST.get('description', '')
            product.stock = request.POST.get('stock', 'In-Stock')

            # Process images
            for i in range(1, 5):
                pic_field = f'pic{i}'
                pic_file = request.FILES.get(pic_field)
                if pic_file:
                    # Delete old image if exists
                    old_pic = getattr(product, pic_field)
                    if old_pic:
                        try:
                            os.remove("media/" + str(old_pic))
                        except OSError:
                            pass
                    # Save new image
                    setattr(product, pic_field, pic_file)

            product.save()
            return HttpResponseRedirect("/profile/")

        # Define color options for template
        colors = ['Red', 'Green', 'Yellow', 'Pink', 'White', 'Black', 
                 'Blue', 'Brown', 'SkyBlue', 'Orange', 'Navy', 'Gray']

        context = {
            "Product": product,
            "Maincategory": maincategories,
            "Subcategory": subcategories,
            "Brand": brands,
            "colors": colors,
        }
        return render(request, "editproduct.html", context)

    except (Product.DoesNotExist, Seller.DoesNotExist):
        return HttpResponseRedirect("/profile/")
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/login/")

def singleproduct(request,num):
    p = Product.objects.get(id=num)
    color = p.color.split(",")
    if color and color[-1] == "":
        color = color[:-1]
    
    from mainApp.models import Review
    reviews = Review.objects.filter(product=p).order_by('-date')
    
    # Calculate average rating
    from django.db.models import Avg
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 5
    rating_count = reviews.count()
    
    # Similar products
    similar_products = Product.objects.filter(maincategory=p.maincategory).exclude(id=p.id)[:6]
    
    # Check if user has already reviewed
    user_review = None
    if request.user.is_authenticated:
        try:
            from mainApp.models import Buyer
            buyer = Buyer.objects.get(username=request.user)
            user_review = reviews.filter(buyer=buyer).first()
        except:
            pass

    context = {
        "Product": p,
        "color": color,
        "reviews": reviews,
        "avg_rating": round(avg_rating, 1),
        "rating_count": rating_count,
        "user_review": user_review,
        "similar_products": similar_products,
    }
    return render(request,"singleproductpage.html", context)

@login_required(login_url='/login/')
def add_review(request, num):
    if request.method == "POST":
        try:
            from mainApp.models import Product, Buyer, Review
            p = Product.objects.get(id=num)
            buyer = Buyer.objects.get(username=request.user)
            rating = request.POST.get('rating', 5)
            comment = request.POST.get('comment')
            image = request.FILES.get('image')
            
            review, created = Review.objects.update_or_create(
                product=p, buyer=buyer,
                defaults={'rating': rating, 'comment': comment}
            )
            if image:
                review.image = image
                review.save()
        except Exception as e:
            print(f"Error adding review: {e}")
            
    return HttpResponseRedirect(f"/single-product-page/{num}/")

@login_required(login_url='/login/')
def toggle_like_review(request, num):
    try:
        from mainApp.models import Review, Buyer
        review = Review.objects.get(id=num)
        buyer = Buyer.objects.get(username=request.user)
        if buyer in review.likes.all():
            review.likes.remove(buyer)
        else:
            review.likes.add(buyer)
        return HttpResponseRedirect(f"/single-product-page/{review.product.id}/")
    except:
        return HttpResponseRedirect("/")

@login_required(login_url='/login/')
def add_reply(request, num):
    if request.method == "POST":
        try:
            from mainApp.models import Review, Reply
            review = Review.objects.get(id=num)
            message = request.POST.get('message')
            user_name = request.user.username
            
            Reply.objects.create(review=review, user_name=user_name, message=message)
            return HttpResponseRedirect(f"/single-product-page/{review.product.id}/")
        except:
            pass
    return HttpResponseRedirect("/")

@login_required(login_url='/login/')
def delete_review(request, num):
    try:
        from mainApp.models import Review
        review = Review.objects.get(id=num)
        from mainApp.models import Buyer
        buyer = Buyer.objects.get(username=request.user)
        if review.buyer == buyer:
            product_id = review.product.id
            review.delete()
            return HttpResponseRedirect(f"/single-product-page/{product_id}/")
    except:
        pass
    return HttpResponseRedirect("/")

def addToWishlist(request,num):
    try:
        buyer = Buyer.objects.get(username=request.user)
        wishlist = Wishlist.objects.filter(buyer=buyer)

        p = Product.objects.get(id=num)
        flag=False
        for i in wishlist:
            if(i.product==p):
                flag=True
                break
        if(flag==False):
            w = Wishlist()
            w.buyer=buyer
            w.product=p
            w.save()
        return HttpResponseRedirect("/profile/")
    except:
        return HttpResponseRedirect("/profile/")
    
@login_required(login_url='/login/')
def deletewishlist(request,num):
    try:
        w = Wishlist.objects.get(id=num)

        buyer = Buyer.objects.get(username=request.user)
        if(w.buyer==buyer):
            w.delete()
        return HttpResponseRedirect("/profile/")
    except:
        return HttpResponseRedirect("/profile/")

   
def AddtoCart(request):
    pid = request.POST.get('pid')
    color = request.POST.get('color')
    cart = request.session.get("cart",None)
    if(cart):
        if(pid in cart.keys() and color==cart[pid][1]):
            pass
        else:
            count = len(cart.keys())
            count=count+1
            cart.setdefault(str(count),[pid,1,color])

    else:
        cart = {"1":[pid,1,color]}
    request.session['cart']=cart
    return HttpResponseRedirect("/cart/")


from django.shortcuts import render, redirect
from .models import Product, Coupon
from django.utils import timezone  # Correct import for Django timezone

def cartPage(request):
    cart = request.session.get("cart", None)
    total = 0
    shipping = 0
    final = 0
    discount_amount = 0
    applied_coupon = None
    
    if cart:
        for values in cart.values():
            p = Product.objects.get(id=int(values[0]))
            total = total + p.finalprice * values[1]
        
        if len(cart.values()) >= 1 and total < 1000:
            shipping = 40
        
        # Check for applied coupon
        coupon_code = request.session.get('applied_coupon', None)
        if coupon_code:
            try:
                applied_coupon = Coupon.objects.get(code=coupon_code)
                if applied_coupon.is_valid(total):
                    discount_amount = (total * applied_coupon.discount) / 100
                else:
                    applied_coupon = None
                    request.session.pop('applied_coupon', None)
            except Coupon.DoesNotExist:
                request.session.pop('applied_coupon', None)
        
        final = total + shipping - discount_amount
    
    # Auto-seed the 20% discount coupon if it does not exist
    try:
        if not Coupon.objects.filter(code="SAVE20").exists():
            Coupon.objects.create(
                code="SAVE20",
                discount=20,
                min_order_amount=400,
                valid_from=timezone.now(),
                valid_to=timezone.now() + timezone.timedelta(days=3650),
                active=True,
                description="Get 20% off on orders above ₹400"
            )
    except Exception:
        pass

    # Get all active coupons
    available_coupons = Coupon.objects.filter(
        active=True,
        valid_from__lte=timezone.now(),  # Correct usage of timezone.now()
        valid_to__gte=timezone.now()     # Correct usage of timezone.now()
    ).order_by('-discount')  # Fixed typo from 'discount' to 'discount'
    
    context = {
        "Cart": cart,
        "Total": total,
        "Shipping": shipping,
        "Final": final,
        "available_coupons": available_coupons,
        "applied_coupon": applied_coupon,
        "discount_amount": discount_amount,
    }
    
    return render(request, "cart.html", context)

def apply_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        request.session['applied_coupon'] = code
    except Coupon.DoesNotExist:
        pass
    return redirect('cartPage')

def remove_coupon(request):
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
    return redirect('cartPage')

def updateCart(request,id,num):
    cart = request.session.get("cart",None)
    if(cart):
        if(num=="-1"):
            if(cart[id][1]>1):
                q = cart[id][1]
                q=q-1
                cart[id][1]=q
        else:
            q = cart[id][1]
            q=q+1
            cart[id][1]=q

        request.session["cart"]=cart
    return HttpResponseRedirect("/cart/")

def deleteCart(request,id):
    cart = request.session.get("cart",None)
    if(cart):
        cart.pop(id)
        request.session['cart']=cart
    return HttpResponseRedirect("/cart/")

# client = razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY))
@login_required(login_url='/login/')
def checkoutPage(request):
    cart = request.session.get("cart",None)
    total = 0
    shipping = 0
    final = 0
    discount_amount = 0
    if(cart):
        for values in cart.values():
            p = Product.objects.get(id=int(values[0]))
            total=total+p.finalprice*values[1]
        if(len(cart.values())>=1 and total<1000):
            shipping=40
            
        # Check for applied coupon
        coupon_code = request.session.get('applied_coupon', None)
        if coupon_code:
            try:
                applied_coupon = Coupon.objects.get(code=coupon_code)
                if applied_coupon.is_valid(total):
                    discount_amount = (total * applied_coupon.discount) / 100
                else:
                    request.session.pop('applied_coupon', None)
            except Coupon.DoesNotExist:
                request.session.pop('applied_coupon', None)
                
        final=total+shipping-discount_amount
    try:
        buyer = Buyer.objects.get(username=request.user)
        if(request.method=="POST"):
            mode = request.POST.get('mode')
            check = Checkout()
            check.buyer=buyer
            check.total=total
            check.shipping=shipping
            check.final=int(final)
            check.save()
            for value in cart.values():
                cp = CheckoutProducts()
                p = Product.objects.get(id=int(value[0]))
                cp.name=p.name
                cp.pic=p.pic1.url
                cp.color=value[2] if value[2] else "None"
                cp.price=p.finalprice
                cp.qty=value[1]
                cp.total=p.finalprice*value[1]
                cp.checkout=check
                cp.seller=p.seller
                cp.save()
            request.session['cart']={}
            if(mode=="COD"):
                return HttpResponseRedirect("/confirmation/")
            else:
                orderAmount = int(check.final*100)
                orderCurrency = "INR"
                paymentOrder = client.order.create(dict(amount=orderAmount,currency=orderCurrency,payment_capture=1))
                paymentId = paymentOrder['id']
                check.mode="Net Banking"
                check.save()
                return render(request,"pay.html",{
                    "amount":orderAmount,
                    "api_key":RAZORPAY_API_KEY,
                    "order_id":paymentId,
                    "User":buyer
                })

        return render(request,"checkOut.html",{"Cart":cart,"Total":total,"Shipping":shipping,"Final":final,"User":buyer})
    except Exception as e:
        print("Exception in checkoutPage:", e)
        import traceback
        traceback.print_exc()
        return HttpResponseRedirect("/profile/")

@login_required(login_url='/login/')
def paymentSuccess(request,rppid,rpoid,rpsid):
    buyer = Buyer.objects.get(username=request.user)
    check = Checkout.objects.filter(buyer=buyer)
    check=check[::-1]
    check=check[0]
    check.rppid=rppid
    check.rpoid=rpoid
    check.rpsid=rpsid
    check.paymentstatus=2
    check.save()
    return HttpResponseRedirect('/confirmation/')

@login_required(login_url='/login/')
def paynow(request, num):
    try:
        buyer = Buyer.objects.get(username=request.user)
    except Buyer.DoesNotExist:
        return HttpResponseRedirect("/profile/")

    # Get the checkout instance or return 404
    check = get_object_or_404(Checkout, id=num)

    try:
        order_amount = int(check.final * 100)  # Razorpay expects amount in paise
        order_currency = "INR"
        payment_order = client.order.create({
            "amount": order_amount,
            "currency": order_currency,
            "payment_capture": 1
        })
        payment_id = payment_order['id']
    except Exception as e:
        print(f"Razorpay Error: {e}")
        return render(request, "error.html", {"message": "Payment Gateway Error!"})

    # Send necessary data to template
    return render(request, "pay.html", {
        "amount": order_amount,
        "api_key": RAZORPAY_API_KEY,
        "order_id": payment_id,
        "User": buyer
    })


# Assuming RAZORPAY_API_KEY and RAZORPAY_API_SECRET contain your actual Razorpay API key and secret

# Now, proceed with your existing code
def paynow(request, num):
    try:
        buyer = get_object_or_404(Buyer, username=request.user)
    except Buyer.DoesNotExist:
        return HttpResponseRedirect("/profile/")
    
    # Try to get the Checkout object or return a 404 page if not found
    check = get_object_or_404(Checkout, id=num)
    
    orderAmount = check.final * 100
    orderCurrency = "INR"
    
    # Assuming `client` is initialized for the Razorpay API
    paymentOrder = client.order.create(dict(amount=orderAmount, currency=orderCurrency, payment_capture=1))
    paymentId = paymentOrder['id']
    
    # Save the Checkout object after modifying it
    check.save()
    
    return render(request, "pay.html", {
        "amount": orderAmount,
        "api_key": RAZORPAY_API_KEY,
        "order_id": paymentId,
        "User": buyer
    })

@login_required(login_url='/login/')
def myOrders(request):
    try:
        buyer = Buyer.objects.get(username=request.user)
        orders = Checkout.objects.filter(buyer=buyer).order_by('-date')
        order_data = []
        for order in orders:
            products = CheckoutProducts.objects.filter(checkout=order)
            order_data.append({'order': order, 'products': products})
        return render(request, 'myOrders.html', {'order_data': order_data, 'User': buyer})
    except Buyer.DoesNotExist:
        return HttpResponseRedirect('/profile/')

@login_required(login_url='/login/')
def myWishlist(request):
    try:
        buyer = Buyer.objects.get(username=request.user)
        wishlist_items = Wishlist.objects.filter(buyer=buyer).select_related('product')
        return render(request, 'myWishlist.html', {'wishlist_items': wishlist_items, 'User': buyer})
    except Buyer.DoesNotExist:
        return HttpResponseRedirect('/profile/')

@login_required(login_url='/login/')
def orderDetail(request, order_id):
    try:
        # Try finding as Buyer first
        try:
            buyer = Buyer.objects.get(username=request.user)
            order = get_object_or_404(Checkout, id=order_id, buyer=buyer)
            user_type = 'buyer'
        except Buyer.DoesNotExist:
            # If not buyer, try as Seller
            seller = Seller.objects.get(username=request.user)
            order = get_object_or_404(Checkout, id=order_id)
            # Verify if this seller has products in this order
            seller_items = CheckoutProducts.objects.filter(checkout=order, seller=seller)
            if not seller_items.exists():
                return HttpResponseRedirect('/profile/')
            user_type = 'seller'
            buyer = order.buyer # For template info

        products = CheckoutProducts.objects.filter(checkout=order)
        # Build tracking steps
        steps = [
            {'label': 'Order Placed',      'icon': 'fas fa-shopping-bag', 'status_val': 1},
            {'label': 'Order Packed',       'icon': 'fas fa-box',          'status_val': 2},
            {'label': 'Out for Delivery',   'icon': 'fas fa-truck',        'status_val': 3},
            {'label': 'Delivered',          'icon': 'fas fa-check-circle', 'status_val': 4},
        ]
        
        cancelled = (order.orderstatus == 0)
        if not cancelled:
            for step in steps:
                step['done']   = order.orderstatus >= step['status_val']
                step['active'] = order.orderstatus == step['status_val']
        
        return render(request, 'orderDetail.html', {
            'order': order,
            'products': products,
            'tracking_steps': steps,
            'cancelled': cancelled,
            'User': buyer,
            'user_type': user_type
        })
    except Exception as e:
        print(f"Error in orderDetail: {e}")
        return HttpResponseRedirect('/profile/')

@login_required(login_url='/login/')
def update_order_status(request, order_id):
    if request.method == "POST":
        try:
            seller = Seller.objects.get(username=request.user)
            order = Checkout.objects.get(id=order_id)
            new_status = request.POST.get('status')
            order.orderstatus = int(new_status)
            order.save()
            messages.success(request, f"Order #{order_id} status updated successfully!")
        except Exception as e:
            messages.error(request, f"Failed to update status: {e}")
    return HttpResponseRedirect(f"/order-detail/{order_id}/")

def confirmationPage(request):
    return render(request,"confirmation.html")
    
def ContactPage(request):
    if request.method == "POST":
        c = Contact()
        c.name = request.POST.get("name")
        c.email = request.POST.get("email")
        c.phone = request.POST.get("phone")
        c.subject = request.POST.get("subject")
        c.massege = request.POST.get("massege")  # Corrected typo from "massege" to "message"
        
        sender_email = "gyanbabu193@gmail.com"
        sender_password = "ulys fufa pbgw fgto"
        recipient_email = "guptagyanprakash8@gmail.com"

        # Create a message object
        massege = MIMEMultipart()
        massege["From"] = sender_email
        massege["To"] = recipient_email
        massege["Subject"] = "Subject of the Email"

        # Email body
        email_body = f"Name: {c.name}\nEmail: {c.email}\nPhone: {c.phone}\nSubject: {c.subject}\nMessage: {c.massege}"
        massege.attach(MIMEText(email_body, "plain"))

        try:
            # SMTP server configuration (for Gmail)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587

            # Create a connection to the SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)

            # Start the TLS connection
            server.starttls()

            # Login to the email account
            server.login(sender_email, sender_password)

            # Send the email
            server.sendmail(sender_email, recipient_email, massege.as_string())

            # Quit the server
            server.quit()

            # print("Email sent successfully!")
            messages.success(request, "Your Query Has Been Submitted!!!! Our Team Will Contact You Soon")

        except Exception as e:
            print(f"Error sending email: {e}")
            messages.error(request, "There was an error sending your query. Please try again later.")

        c.save()
        return render(request, "contact.html")
    else:
        return render(request, "contact.html")

def AboutPage(request):
    return render(request,"about.html")

    
    
def forgetUsername(request):
    return render(request,"forgetpws.html")



@csrf_exempt
@require_POST
def start_chat(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        # Create or get chat session
        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={}
        )
        
        # Create welcome message if new session
        if created:
            ChatMessage.objects.create(
                session=session,
                message="Hi there! 👋 I'm your shopping assistant. How can I help you today?",
                is_bot=True
            )
        
        # Get all messages for this session
        messages = session.messages.order_by('created_at').values(
            'id', 'message', 'is_bot', 'created_at'
        )
        
        return JsonResponse({
            'status': 'success',
            'session_id': session_id,
            'messages': list(messages),
            'is_new_session': created
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_POST
def handle_message(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        message = data.get('message', '').strip()
        
        if not session_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Session ID is required'
            }, status=400)
            
        if not message:
            return JsonResponse({
                'status': 'error',
                'message': 'Message cannot be empty'
            }, status=400)
        
        # Get session
        try:
            session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid session ID'
            }, status=404)
        
        # Save user message
        ChatMessage.objects.create(
            session=session,
            message=message,
            is_bot=False
        )
        
        # Generate bot response
        bot_response = generate_bot_response(message, session)
        
        # Handle clear chat action
        if 'actions' in bot_response and 'clear_chat' in bot_response['actions']:
            # Clear all messages for this session
            session.messages.all().delete()
            # Recreate the welcome message
            ChatMessage.objects.create(
                session=session,
                message=bot_response['text'],
                is_bot=True
            )
        else:
            # Save normal bot response
            ChatMessage.objects.create(
                session=session,
                message=bot_response['text'],
                is_bot=True
            )
        
        return JsonResponse({
            'status': 'success',
            'response': bot_response
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
def generate_bot_response(user_message, session=None):
    user_message = user_message.lower()
    
    # Enhanced responses with more options
    responses = {
        'track': {
            'text': 'You can track your order in "My Orders" section. Would you like me to show your recent orders?',
            'quick_replies': ['Show my orders', 'Track by order ID', 'Contact support'],
            'actions': ['show_orders']
        },
        'return': {
            'text': 'We offer 30-day easy returns. Please keep the product in original condition with tags attached.',
            'quick_replies': ['Initiate return', 'Check return status', 'Download return label'],
            'actions': ['start_return']
        },
        'payment': {
            'text': 'For payment issues, you can check payment methods or contact our support team at payments@onlinebazar.com',
            'quick_replies': ['Payment options', 'Failed payment help', 'Refund status'],
            'actions': ['payment_help']
        },
        'clear': {
            'text': 'Chat history has been cleared. How can I help you now?',
            'quick_replies': ['Track order', 'Return product', 'Payment issue'],
            'actions': ['clear_chat']
        },
        'hi': {
            'text': 'Hello! 👋 Welcome to OnlineBazar support. I can help with orders, returns, payments and more!',
            'quick_replies': ['Track my order', 'Return policy', 'Payment issues'],
            'actions': ['welcome']
        },
        'thank': {
            'text': 'You\'re welcome! 😊 Is there anything else I can help you with today?',
            'quick_replies': ['No, thank you', 'Yes, need more help', 'Rate this chat'],
            'actions': ['thank_you']
        }
    }
    
    # Check for specific commands first
    if 'clear' in user_message or 'reset' in user_message:
        if session:
            session.messages.all().delete()
        return responses['clear']
    
    if any(greet in user_message for greet in ['hi', 'hello', 'hey']):
        return responses['hi']
    
    if any(thank in user_message for thank in ['thank', 'thanks', 'appreciate']):
        return responses['thank']
    
    # Check for other keywords
    for keyword, response in responses.items():
        if keyword in user_message:
            return response
    
    # Default response with more options
    return {
        'text': 'I can help you with:',
        'quick_replies': [
            'Track my order',
            'Start a return',
            'Payment issues',
            'Clear chat history',
            'Talk to human agent'
        ],
        'actions': ['show_options']
    }