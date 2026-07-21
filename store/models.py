from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """A product category, e.g. Bags, Shoes, Accessories, Wholesale, New Arrivals."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers appear first in menus.'
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:category_detail', args=[self.slug])


class Product(models.Model):
    """A single item for sale (a pair of shoes, a bag, a fabric bundle, etc.)."""

    GENDER_CHOICES = [
        ('unisex', 'Men & Women'),
        ('men', 'Men'),
        ('women', 'Women'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.CASCADE
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Optional. Set an old price here to show a strikethrough discount.'
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex')
    is_sold_out = models.BooleanField(default=False)
    is_active = models.BooleanField(
        default=True,
        help_text='Untick to hide this product from the site without deleting it.'
    )
    is_featured = models.BooleanField(
        default=False,
        help_text='Feature this product on the home page.'
    )
    stock_note = models.CharField(
        max_length=120, blank=True,
        help_text='Optional short note, e.g. "Only 2 left" or "Made to order".'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:200]
            slug_candidate = base_slug
            counter = 1
            while Product.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                counter += 1
                slug_candidate = f'{base_slug}-{counter}'
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    @property
    def main_image(self):
        first = self.images.first()
        return first.image if first else None

    @property
    def is_on_sale(self):
        return bool(self.compare_at_price and self.compare_at_price > self.price)


class ProductImage(models.Model):
    """One of possibly several photos for a product. First by `order` is the main photo."""

    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/')
    alt_text = models.CharField(
        max_length=200, blank=True,
        help_text='Short description for accessibility, e.g. "Brown leather loafers, side view".'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'Image for {self.product.name}'


class Order(models.Model):
    """
    A "Order on WhatsApp" enquiry placed from the site. Payment itself happens
    on WhatsApp, so this record exists so the business always has a copy of
    who asked for what, even if a WhatsApp chat gets lost or deleted.
    """

    STATUS_NEW = 'new'
    STATUS_CONTACTED = 'contacted'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_CONTACTED, 'Contacted on WhatsApp'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    note = models.TextField(blank=True, help_text='Anything extra the customer added.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} – {self.customer_name}'

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_value(self):
        return sum(item.quantity * item.unit_price for item in self.items.all())


class OrderItem(models.Model):
    """A single product+quantity line inside an Order."""

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name='order_items', on_delete=models.SET_NULL, null=True
    )
    # Snapshots so the order stays accurate even if the product is later
    # edited, its price changes, or it gets deleted.
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product_name}'

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


class WholesaleEnquiry(models.Model):
    """A "Become a Wholesale Partner" form submission from a boutique owner."""

    business_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    estimated_monthly_quantity = models.CharField(
        max_length=100,
        help_text='e.g. "50-100 pieces" or "20 pairs of shoes a month".'
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    contacted = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Wholesale enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.business_name} ({self.created_at:%d %b %Y})'
