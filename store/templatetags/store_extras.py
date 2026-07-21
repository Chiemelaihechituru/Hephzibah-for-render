from urllib.parse import quote

from django import template
from django.conf import settings

register = template.Library()


# Royalty-free Unsplash photos used to represent each product category on the
# homepage "seals" (replacing the old single-letter badges). Keyed by
# Category.slug. Each URL is cropped to a square via Unsplash's imgix params
# so it drops cleanly into the circular seal frame.
CATEGORY_IMAGES = {
    'bags': (
        'https://images.unsplash.com/photo-1598532163257-ae3c6b2524b6'
        '?w=300&h=300&fit=crop&crop=entropy&q=80&auto=format'
    ),
    'shoes': (
        'https://images.unsplash.com/photo-1490114538077-0a7f8cb49891'
        '?w=300&h=300&fit=crop&crop=entropy&q=80&auto=format'
    ),
    'accessories': (
        'https://images.unsplash.com/photo-1758995115682-1452a1a9e35b'
        '?w=300&h=300&fit=crop&crop=entropy&q=80&auto=format'
    ),
    'wholesale': (
        'https://images.unsplash.com/photo-1757837593538-b4a8654132f1'
        '?w=300&h=300&fit=crop&crop=entropy&q=80&auto=format'
    ),
    'new-arrivals': (
        'https://images.unsplash.com/photo-1772570824145-e996a55204fb'
        '?w=300&h=300&fit=crop&crop=entropy&q=80&auto=format'
    ),
}


@register.filter
def category_image(slug):
    """Looks up a representative Unsplash photo for a category slug.

    Returns None for any slug that isn't mapped yet (e.g. a brand-new
    category an admin just added), so the template can gracefully fall
    back to the original lettered seal instead of showing a broken image.
    """
    return CATEGORY_IMAGES.get(slug)


@register.filter
def naira(value):
    """Formats a number as a Naira amount: 15000 -> '₦15,000'."""
    try:
        return f'₦{float(value):,.0f}'
    except (TypeError, ValueError):
        return value


@register.simple_tag
def whatsapp_product_link(product):
    """A quick 'ask about this on WhatsApp' link, used on product cards."""
    text = quote(
        f"Hello {settings.BUSINESS_NAME}, is the \"{product.name}\" "
        f"(₦{product.price:,.0f}) still available?"
    )
    return f'https://wa.me/{settings.BUSINESS_WHATSAPP}?text={text}'
