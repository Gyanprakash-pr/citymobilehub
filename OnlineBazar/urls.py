from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

admin.site.site_title="Desi Mobile"
admin.site.site_header="Desi Mobile"
# admin.site.site_url="Online Bazar"
from mainApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('seed-store/', views.seed_store),
    path('',views.Homepage),
    path('shop/<str:mc>/<str:sc>/<str:br>/',views.ShopPage),
    path('login/', views.Login, name='login'),

    path('logout/',views.logout),
    path('signup/',views.SignUp),
    path('profile/',views.ProfilePage),
    path('updateProfile/',views.updateProfilePage),
    path('add-product/',views.addproduct),
    path('delete-product/<int:num>/',views.deleteproduct),
    path('edit-product/<int:num>/',views.Editproduct),
    path('single-product-page/<int:num>/',views.singleproduct),
    path('add-review/<int:num>/', views.add_review, name='add_review'),
    path('toggle-like-review/<int:num>/', views.toggle_like_review, name='toggle_like_review'),
    path('add-reply/<int:num>/', views.add_reply, name='add_reply'),
    path('delete-review/<int:num>/', views.delete_review, name='delete_review'),
    path('add-to-wishlist/<int:num>/',views.addToWishlist),
    path('delete-wishlist/<int:num>/',views.deletewishlist),
    path('add-to-cart/',views.AddtoCart),
    # path('cart/',views.cartPage),

    path('cart/', views.cartPage, name='cartPage'),  # Add name='cart'
    path('apply-coupon/<str:code>/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),

    path('update-cart/<str:id>/<str:num>/',views.updateCart),
    path('delete-cart/<str:id>/',views.deleteCart),
    path('checkout/',views.checkoutPage),
    path('confirmation/',views.confirmationPage),
    path('orders/', views.myOrders, name='myOrders'),
    path('wishlist/', views.myWishlist, name='myWishlist'),
    path('order-detail/<int:order_id>/', views.orderDetail, name='orderDetail'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    # path('paymentSuccess/<str:rppid>/<str:rpoid>/<str:rpsid>/',views.paymentSuccess),
    path('paynow/<int:num>/',views.paynow),
    path('contact/',views.ContactPage),
    path('forget-username/',views.forgetUsername),
    # path('forget-otp/',views.forgetOTP),
    # path('forget-password/',views.forgetPassword),
    path("forget-password/", views.ForgetPassword),
    path('about/',views.AboutPage),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
  
    
    path('chatbot/start-chat/', views.start_chat, name='start_chat'),
    path('chatbot/send-message/', views.handle_message, name='handle_message'),
    
    # Allauth Social Login
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
