from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Order, OrderItem, Product, ProductImage, WholesaleEnquiry


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'product_count')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class ProductImageInline(admin.TabularInline):
    """Lets an admin upload/reorder several photos for one product in one screen."""
    model = ProductImage
    extra = 3
    fields = ('image', 'preview', 'alt_text', 'order')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:6px;" />', obj.image.url
            )
        return '—'
    preview.short_description = 'Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail', 'name', 'category', 'price', 'is_sold_out',
        'is_active', 'is_featured', 'gender', 'created_at',
    )
    list_display_links = ('name',)
    list_editable = ('price', 'is_sold_out', 'is_active', 'is_featured')
    list_filter = ('category', 'is_sold_out', 'is_active', 'is_featured', 'gender')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    actions = ['mark_sold_out', 'mark_available']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'gender', 'description')
        }),
        ('Pricing & stock', {
            'fields': ('price', 'compare_at_price', 'stock_note', 'is_sold_out', 'is_active', 'is_featured')
        }),
    )

    def thumbnail(self, obj):
        image = obj.main_image
        if image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', image.url)
        return '—'
    thumbnail.short_description = ''

    @admin.action(description='Mark selected products as sold out')
    def mark_sold_out(self, request, queryset):
        updated = queryset.update(is_sold_out=True)
        self.message_user(request, f'{updated} product(s) marked as sold out.')

    @admin.action(description='Mark selected products as available')
    def mark_available(self, request, queryset):
        updated = queryset.update(is_sold_out=False)
        self.message_user(request, f'{updated} product(s) marked as available.')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'unit_price', 'quantity', 'subtotal')
    can_delete = False

    def subtotal(self, obj):
        return f'₦{obj.subtotal:,.0f}'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer_name', 'phone_number', 'items_summary',
        'total_value_display', 'status', 'created_at',
    )
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'phone_number', 'address')
    readonly_fields = ('customer_name', 'phone_number', 'address', 'created_at')
    inlines = [OrderItemInline]

    def items_summary(self, obj):
        return ', '.join(f'{i.quantity}x {i.product_name}' for i in obj.items.all())
    items_summary.short_description = 'Items ordered'

    def total_value_display(self, obj):
        return f'₦{obj.total_value:,.0f}'
    total_value_display.short_description = 'Total'

    def has_add_permission(self, request):
        # Orders only ever come in through the website's WhatsApp order form.
        return False


@admin.register(WholesaleEnquiry)
class WholesaleEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        'business_name', 'contact_name', 'location', 'phone_number',
        'estimated_monthly_quantity', 'contacted', 'created_at',
    )
    list_editable = ('contacted',)
    list_filter = ('contacted', 'created_at')
    search_fields = ('business_name', 'contact_name', 'location', 'phone_number', 'email')
    readonly_fields = (
        'business_name', 'contact_name', 'location', 'phone_number',
        'email', 'estimated_monthly_quantity', 'message', 'created_at',
    )

    def has_add_permission(self, request):
        return False
