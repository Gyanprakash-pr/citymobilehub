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

import razorpay 
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from .models import Buyer, Checkout  # Import your models here
from django.conf import settings
from OnlineBazar.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY
client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))



from .models import *


def Homepage(request):
    products = Product.objects.all()
    products=products[::-1]
    if(request.method=='POST'):
        try:
            email = request.POST.get("email")
            n = Newslatter()
            n.email=email
            n.save()
        except:
            pass
        return HttpResponseRedirect("/")
    return render(request,"index.html",{"Product":products})

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
            products = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc))
        elif(mc=="All" and sc!="All" and br=="All"):
            products = Product.objects.filter(subcategory=Subcategory.objects.get(name=sc))
        elif(mc=="All" and sc=="All" and br!="All"):
            products = Product.objects.filter(brand=Brand.objects.get(name=br))
        elif(mc!="All" and sc!="All" and br=="All"):
            products = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),subcategory=Subcategory.objects.get(name=sc))
        elif(mc!="All" and sc=="All" and br!="All"):
            products = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),brand=Brand.objects.get(name=br))
        elif(mc=="All" and sc!="All" and br!="All"):
            products = Product.objects.filter(subcategory=Subcategory.objects.get(name=sc),brand=Brand.objects.get(name=br))
        elif(mc!="All" and sc!="All" and br!="All"):
            products = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),subcategory=Subcategory.objects.get(name=sc),brand=Brand.objects.get(name=br))

    products=products[::-1]
    return render(request,"shop.html",{"Product":products,
                                      "Maincategory":maincategory,
                                      "Subcategory":subcategory,
                                      "Brand":brand,
                                      "mc":mc,"sc":sc,"br":br
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
            return render(request,"sellerprofile.html",{"User":seller,"products":products})
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
        size=""
        if(request.POST.get("M")):
            size=size+"M,"
        if(request.POST.get("L")):
            size=size+"L,"
        if(request.POST.get("SM")):
            size=size+"SM,"
        if(request.POST.get("XL")):
            size=size+"XL,"
        if(request.POST.get("XXL")):
            size=size+"XXL,"
        if(request.POST.get("6")):
            size=size+"6,"
        if(request.POST.get("7")):
            size=size+"7,"
        if(request.POST.get("8")):
            size=size+"8,"
        if(request.POST.get("9")):
            size=size+"9,"
        if(request.POST.get("10")):
            size=size+"10,"
        if(request.POST.get("11")):
            size=size+"11,"
        if(request.POST.get("12")):
            size=size+"12,"
        p.color=color
        p.size=size




        p.description = request.POST.get('description')
        p.stock = request.POST.get('stock')
        p.pic1 = request.FILES.get('pic1')
        p.pic2 = request.FILES.get('pic2')
        p.pic3 = request.FILES.get('pic3')
        p.pic4 = request.FILES.get('pic4')
        try:
            p.seller = Seller.objects.get(username=request.user)
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

            # Process sizes
            available_sizes = ['M', 'L', 'SM', 'XL', 'XXL', '6', '7', '8', '9', '10', '11', '12']
            selected_sizes = [size for size in available_sizes if request.POST.get(size)]
            product.size = ",".join(selected_sizes) + "," if selected_sizes else ""

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

        # Define color and size options for template
        colors = ['Red', 'Green', 'Yellow', 'Pink', 'White', 'Black', 
                 'Blue', 'Brown', 'SkyBlue', 'Orange', 'Navy', 'Gray']
        sizes = ['M', 'L', 'SM', 'XL', 'XXL', '6', '7', '8', '9', '10', '11', '12']

        context = {
            "Product": product,
            "Maincategory": maincategories,
            "Subcategory": subcategories,
            "Brand": brands,
            "colors": colors,
            "sizes": sizes,
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
    color = color[:-1]
    size = p.size.split(",")
    size = size[:-1]
    
    
    return render(request,"singleproductpage.html",{"Product":p,"color":color,"size":size})

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
    size = request.POST.get('size')
    cart = request.session.get("cart",None)
    if(cart):
        if(pid in cart.keys() and color==cart[pid][1] and size==cart[pid][2]):
            pass
        else:
            count = len(cart.keys())
            count=count+1
            cart.setdefault(str(count),[pid,1,color,size])

    else:
        cart = {"1":[pid,1,color,size]}
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
    if(cart):
        for values in cart.values():
            p = Product.objects.get(id=int(values[0]))
            total=total+p.finalprice*values[1]
        if(len(cart.values())>=1 and total<1000):
            shipping=40
        final=total+shipping
    try:
        buyer = Buyer.objects.get(username=request.user)
        if(request.method=="POST"):
            mode = request.POST.get('mode')
            check = Checkout()
            check.buyer=buyer
            check.total=total
            check.shipping=shipping
            check.final=final
            check.save()
            for value in cart.values():
                cp = CheckoutProducts()
                p = Product.objects.get(id=int(value[0]))
                cp.name=p.name
                cp.pic=p.pic1.url
                cp.size=value[3]
                cp.color=value[2]
                cp.price=p.finalprice
                cp.qty=value[1]
                cp.total=p.finalprice*value[1]
                cp.checkout=check
                cp.save()
            request.session['cart']={}
            if(mode=="COD"):
                return HttpResponseRedirect("/confirmation/")
            else:
                orderAmount = check.final*100
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
    except:
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