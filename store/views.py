import json
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static as static_url

from .forms import OrderForm, WholesaleEnquiryForm
from .models import Category, Order, OrderItem, Product


PRODUCTS_PER_PAGE = 12

# (url param value, order_by field, human label)
SORT_OPTIONS = [
    ('newest', '-created_at', 'Newest'),
    ('price_asc', 'price', 'Price: Low to High'),
    ('price_desc', '-price', 'Price: High to Low'),
    ('name_asc', 'name', 'Name: A-Z'),
]
SORT_LOOKUP = {value: field for value, field, _label in SORT_OPTIONS}

GENDER_FILTERS = [
    ('', 'All'),
    ('women', 'Women'),
    ('men', 'Men'),
    ('unisex', 'Men & Women'),
]

# Characters that are unsafe to embed raw inside a <script> tag, escaped the
# same way Django's own json_script() does it, so structured data can never
# break out of its script tag or execute as HTML/JS.
_JSONLD_ESCAPES = {ord('>'): '\\u003E', ord('<'): '\\u003C', ord('&'): '\\u0026'}


def _safe_jsonld(data):
    """Serializes a dict to a JSON-LD string that's safe to embed in <script type="application/ld+json">."""
    return json.dumps(data, ensure_ascii=True).translate(_JSONLD_ESCAPES)


def _visible_products():
    """Products that should ever be shown to a customer."""
    return Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')


def _product_list_response(request, products, *, template, category=None, page_title, search_query=None):
    """
    Shared by category_detail / all_products / search: applies the search
    query, gender filter, in-stock filter and sort chosen via querystring,
    paginates the result, and renders the shared product-grid template.
    """
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )
        search_query = query
        page_title = f'"{query}" in {category.name}' if category else f'Search results for "{query}"'

    gender = request.GET.get('gender', '')
    if gender in ('men', 'women', 'unisex'):
        products = products.filter(gender=gender)

    in_stock_only = request.GET.get('in_stock') == '1'
    if in_stock_only:
        products = products.filter(is_sold_out=False)

    sort = request.GET.get('sort', 'newest')
    if sort not in SORT_LOOKUP:
        sort = 'newest'
    products = products.order_by(SORT_LOOKUP[sort])

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Preserve every current filter/sort/search param except `page`, so
    # pagination links don't reset whatever the customer chose.
    carried_params = request.GET.copy()
    carried_params.pop('page', None)
    base_querystring = carried_params.urlencode()

    context = {
        'category': category,
        'products': page_obj,
        'page_obj': page_obj,
        'page_title': page_title,
        'search_query': search_query,
        'sort': sort,
        'sort_options': SORT_OPTIONS,
        'gender': gender,
        'gender_filters': GENDER_FILTERS,
        'in_stock_only': in_stock_only,
        'base_querystring': base_querystring,
    }
    return render(request, template, context)


def home(request):
    featured = _visible_products().filter(is_featured=True)[:8]
    if not featured:
        featured = _visible_products()[:8]
    new_arrivals = _visible_products().order_by('-created_at')[:8]
    categories = Category.objects.all()

    business_jsonld = _safe_jsonld({
        "@context": "https://schema.org",
        "@type": "ClothingStore",
        "name": settings.BUSINESS_NAME,
        "image": request.build_absolute_uri(static_url('images/logo.png')),
        "url": request.build_absolute_uri('/'),
        "telephone": settings.BUSINESS_PHONE_DISPLAY,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": settings.BUSINESS_ADDRESS,
            "addressCountry": "NG",
        },
    })

    context = {
        'featured_products': featured,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'page_title': None,
        'business_jsonld': business_jsonld,
    }
    return render(request, 'store/home.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = _visible_products().filter(category=category)
    return _product_list_response(
        request, products, template='store/category.html',
        category=category, page_title=category.name,
    )


def all_products(request):
    products = _visible_products()
    return _product_list_response(
        request, products, template='store/category.html',
        category=None, page_title='All Products',
    )


def search(request):
    query = request.GET.get('q', '').strip()
    products = _visible_products() if query else Product.objects.none()
    title = f'Search results for "{query}"' if query else 'Search'
    return _product_list_response(
        request, products, template='store/category.html',
        category=None, page_title=title, search_query=query,
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'),
        slug=slug, is_active=True,
    )

    if request.method == 'POST' and not product.is_sold_out:
        form = OrderForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            order = Order.objects.create(
                customer_name=form.cleaned_data['customer_name'],
                phone_number=form.cleaned_data['phone_number'],
                address=form.cleaned_data['address'],
                note=form.cleaned_data['note'],
            )
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                unit_price=product.price,
                quantity=quantity,
            )

            message_lines = [
                f"Hello {settings.BUSINESS_NAME}, I'd like to order:",
                f"- {product.name} (₦{product.price:,.0f}) x{quantity}",
                "",
                f"Name: {form.cleaned_data['customer_name']}",
                f"Phone: {form.cleaned_data['phone_number']}",
                f"Address: {form.cleaned_data['address']}",
            ]
            if form.cleaned_data['note']:
                message_lines.append(f"Note: {form.cleaned_data['note']}")
            message_lines.append("")
            message_lines.append("Please share the payment details. Thank you!")
            whatsapp_text = quote('\n'.join(message_lines))
            whatsapp_url = f'https://wa.me/{settings.BUSINESS_WHATSAPP}?text={whatsapp_text}'
            return redirect(whatsapp_url)
    else:
        form = OrderForm()

    related_products = (
        _visible_products()
        .filter(category=product.category)
        .exclude(pk=product.pk)[:4]
    )

    image_urls = [request.build_absolute_uri(img.image.url) for img in product.images.all()]
    if not image_urls:
        image_urls = [request.build_absolute_uri(static_url('images/logo.png'))]

    product_jsonld = _safe_jsonld({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "description": product.description or product.name,
        "image": image_urls,
        "sku": str(product.pk),
        "category": product.category.name,
        "offers": {
            "@type": "Offer",
            "url": request.build_absolute_uri(product.get_absolute_url()),
            "priceCurrency": "NGN",
            "price": str(product.price),
            "availability": (
                "https://schema.org/OutOfStock" if product.is_sold_out
                else "https://schema.org/InStock"
            ),
        },
    })

    context = {
        'product': product,
        'form': form,
        'related_products': related_products,
        'page_title': product.name,
        'product_jsonld': product_jsonld,
    }
    return render(request, 'store/product_detail.html', context)


def wholesale(request):
    if request.method == 'POST':
        form = WholesaleEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()

            # Try to email the team too, if SMTP has been configured.
            # If it's not configured, EMAIL_BACKEND just prints to the console,
            # so this never blocks the customer's submission from succeeding.
            if settings.WHOLESALE_NOTIFY_EMAIL:
                from django.core.mail import send_mail
                try:
                    send_mail(
                        subject=f'New wholesale enquiry: {enquiry.business_name}',
                        message=(
                            f'Business: {enquiry.business_name}\n'
                            f'Contact: {enquiry.contact_name}\n'
                            f'Location: {enquiry.location}\n'
                            f'Phone: {enquiry.phone_number}\n'
                            f'Email: {enquiry.email}\n'
                            f'Estimated monthly quantity: {enquiry.estimated_monthly_quantity}\n\n'
                            f'Message:\n{enquiry.message}'
                        ),
                        from_email=None,
                        recipient_list=[settings.WHOLESALE_NOTIFY_EMAIL],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            message_lines = [
                f"Hello {settings.BUSINESS_NAME}, I'd like to become a wholesale partner.",
                f"Business name: {enquiry.business_name}",
                f"Location: {enquiry.location}",
                f"Phone: {enquiry.phone_number}",
                f"Estimated monthly order quantity: {enquiry.estimated_monthly_quantity}",
            ]
            if enquiry.message:
                message_lines.append(f"Message: {enquiry.message}")
            whatsapp_text = quote('\n'.join(message_lines))
            whatsapp_url = f'https://wa.me/{settings.BUSINESS_WHATSAPP}?text={whatsapp_text}'

            messages.success(
                request,
                "Thanks! Your wholesale enquiry has been received. "
                "We're redirecting you to WhatsApp to chat with our team directly."
            )
            return redirect(whatsapp_url)
    else:
        form = WholesaleEnquiryForm()

    context = {
        'form': form,
        'page_title': 'Become a Wholesale Partner',
    }
    return render(request, 'store/wholesale.html', context)


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
