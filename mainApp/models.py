
from datetime import timezone
import email
# from re import M
from secrets import choice
from django.db import models


class Maincategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name



class Seller(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=15)
    addressline1 = models.CharField(max_length=100,default=None,null=True,blank=True)
    pin = models.CharField(max_length=100,default=None,null=True,blank=True)
    city = models.CharField(max_length=100,default=None,null=True,blank=True)
    state = models.CharField(max_length=100,default=None,null=True,blank=True)
    pic = models.FileField(upload_to='images',default="non.png",null=True,blank=True)

    def __str__(self):
        return str(self.id)+" "+self.username

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    maincategory = models.ForeignKey(Maincategory,on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory,on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller,on_delete=models.CASCADE,default=None)
    baseprice = models.IntegerField()

    discount = models.IntegerField()
    finalprice = models.IntegerField()
    size = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    description = models.TextField()
    stock = models.CharField(max_length=20,default="In stock")
    pic1 = models.ImageField(upload_to="images",default="no.png",null=True,blank=True)
    pic2 = models.ImageField(upload_to="images",default="no.png",null=True,blank=True)
    pic3 = models.ImageField(upload_to="images",default="no.png",null=True,blank=True)
    pic4 = models.ImageField(upload_to="images",default="no.png",null=True,blank=True)

    def __str__(self):
        return str(self.id)+" "+self.name


class Buyer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=15)
    addressline1 = models.CharField(max_length=100,default=None,null=True,blank=True)
    pin = models.CharField(max_length=100,default=None,null=True,blank=True)
    city = models.CharField(max_length=100,default=None,null=True,blank=True)
    state = models.CharField(max_length=100,default=None,null=True,blank=True)
    pic = models.FileField(upload_to='images',default="non.png",null=True,blank=True)

    def __str__(self):
        return str(self.id)+" "+self.username

class Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(Buyer,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)+" "+self.buyer.username
        
order = ((0,"Cancel"),(1,"Not Packed"),(2,"Packed"),(3,"Out for Delivery"),(4,"Delivered"))
payment = ((1,"pending"),(2,"Done"))

class Checkout(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.IntegerField()
    shipping = models.IntegerField()
    final = models.IntegerField()
    buyer = models.ForeignKey(Buyer,on_delete=models.CASCADE)
    mode = models.CharField(max_length=20,default="COD")
    orderstatus = models.IntegerField(choices=order,default=1)
    paymentstatus = models.IntegerField(choices=payment,default=1)
    rppid = models.CharField(max_length=100,default="",null=True,blank=True)
    rpoid = models.CharField(max_length=100,default="",null=True,blank=True)
    rpsid = models.CharField(max_length=100,default="",null=True,blank=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)+" "+self.buyer.username
    
class CheckoutProducts(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=20)
    price = models.IntegerField()
    qty = models.IntegerField()
    total = models.IntegerField()
    pic = models.CharField(max_length=100)
    checkout = models.ForeignKey(Checkout,on_delete=models.CASCADE)

    def __str__(self):
        return "pid = "+str(self.id)+" Checkout Id = "+str(self.checkout.id)

class Newslatter(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=50,unique=True)

    def __str__(self):
        return self.email
contactstatuschoice = ((1,"active"),(2,"Done"))
class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=15)
    subject = models.TextField(max_length=50)
    massege = models.TextField(max_length=50)
    status = models.IntegerField(choices=contactstatuschoice,default=1)

    def __str__(self):
        return str(self.id)+" "+self.email+" "+self.subject


from django.db import models
from django.utils import timezone  # Add this import

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.PositiveIntegerField(help_text="Percentage discount")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} ({self.discount}% off)"

    def is_valid(self, order_total):
        now = timezone.now()  # Using Django's timezone.now()
        return (self.active and 
                self.valid_from <= now <= self.valid_to and
                order_total >= self.min_order_amount)

    class Meta:
        ordering = ['-discount']


