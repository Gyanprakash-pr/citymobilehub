from rest_framework import serializers
from .models import *

class MaincategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Maincategory
        fields = '__all__'

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['id', 'name', 'username', 'email', 'phone', 'pic']

class ProductSerializer(serializers.ModelSerializer):
    maincategory_name = serializers.ReadOnlyField(source='maincategory.name')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.name')
    brand_name = serializers.ReadOnlyField(source='brand.name')
    seller_name = serializers.ReadOnlyField(source='seller.name')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'maincategory', 'maincategory_name', 
            'subcategory', 'subcategory_name', 'brand', 'brand_name', 
            'seller', 'seller_name', 'baseprice', 'discount', 'finalprice', 
            'color', 'description', 'stock', 'warranty', 'guarantee', 
            'pic1', 'pic2', 'pic3', 'pic4'
        ]
