from django.contrib import admin
from .models import Product, Category
from .models import Order, OrderItem, Payment
from django.utils.html import format_html

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'rating', 'product_image')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'price', 'stock', 'rating')
    list_editable = ('price', 'stock', 'rating')

    def product_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height:50px;" />'.format(obj.image.url))
        return ""

    product_image.short_description = 'Image'



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No extra blank fields for OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'location', 'phone', 'total_amount', 'order_date')
    list_filter = ('order_date', 'user')  # Filter by user and order date
    search_fields = ('user__username', 'location', 'phone')  # Search by user, location, and phone
    inlines = [OrderItemInline]  # Display related OrderItems inline

admin.site.register(Order, OrderAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_id', 'amount', 'payment_date', 'payment_method', 'status')
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'order_id')

admin.site.register(Payment, PaymentAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
