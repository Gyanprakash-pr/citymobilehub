from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .api_views import *

router = DefaultRouter()
router.register(r'maincategories', MaincategoryViewSet)
router.register(r'subcategories', SubcategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('get-token/', obtain_auth_token),
    path('', include(router.urls)),
]
