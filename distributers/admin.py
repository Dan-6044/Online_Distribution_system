from django.contrib import admin
from .models import Product, Category, ReturnItem
from .models import Order, OrderItem, Payment
from django.urls import path
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from .models import ChatMessage
from django.urls import reverse

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


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_admin', 'timestamp', 'reply_button')
    readonly_fields = ('user', 'message', 'is_admin', 'timestamp')
    list_filter = ('is_admin', 'user')

    def get_urls(self):
        # Get the default admin urls and add the custom reply URL
        urls = super().get_urls()
        custom_urls = [
            path('reply/<int:chat_message_id>/', self.admin_site.admin_view(self.reply_to_user), name='reply-to-user'),
        ]
        return custom_urls + urls

    def reply_button(self, obj):
        if not obj.is_admin:  # Show the reply button only for user messages
            # Create the absolute URL for the reply link
            reply_url = reverse('admin:reply-to-user', args=[obj.id])
            return format_html('<a class="button" href="{}">Reply</a>', reply_url)
        return '-'

    reply_button.short_description = 'Reply'

    def reply_to_user(self, request, chat_message_id):
        # Get the message to reply to
        chat_message = get_object_or_404(ChatMessage, id=chat_message_id)

        if request.method == 'POST':
            admin_reply = request.POST.get('admin_reply')

            # Create the admin's reply message
            ChatMessage.objects.create(
                user=chat_message.user,
                message=admin_reply,
                is_admin=True
            )

            self.message_user(request, f'Reply sent to {chat_message.user.username}')
            return HttpResponseRedirect('/admin/distributers/chatmessage/')  # Redirect to the message list

        context = dict(
            self.admin_site.each_context(request),
            chat_message=chat_message,
        )
        return TemplateResponse(request, "reply_to_user.html", context)

# Register ChatMessage with the custom admin view
admin.site.register(ChatMessage, ChatMessageAdmin)


@admin.register(ReturnItem)
class ReturnItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'reason', 'return_date')  # Fields to display in the list view
    search_fields = ('order__id', 'item__product_name', 'reason')  # Enable searching by order ID, item name, and reason
    list_filter = ('return_date',)  # Enable filtering by return date

    # Optionally, you can customize the form layout, fieldsets, etc.
    fieldsets = (
        (None, {
            'fields': ('order', 'item', 'reason')
        }),
        ('Return Information', {
            'fields': ('return_date',)
        }),
    )