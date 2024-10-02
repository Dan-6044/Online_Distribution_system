from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='products'),
    path('product/<int:id>/', views.product_details, name='product_details'),
     path('cart/', views.cart_view, name='cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('update_cart_item/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('delete_cart_item/<int:cart_item_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('submit_order/', views.submit_order, name='submit_order'),
      path('complete-payment/', views.complete_payment, name='complete_payment'),
       path('get-chat-messages/', views.get_chat_messages, name='get_chat_messages'),
    path('post-chat-message/', views.post_chat_message, name='post_chat_message'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)