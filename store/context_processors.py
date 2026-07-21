from urllib.parse import quote

from django.conf import settings

from .models import Category


def business_info(request):
    """Makes business contact details available in every template."""
    greeting = quote(
        f"Hello {settings.BUSINESS_NAME}, I have a question about your products."
    )
    return {
        'BUSINESS_NAME': settings.BUSINESS_NAME,
        'BUSINESS_ADDRESS': settings.BUSINESS_ADDRESS,
        'BUSINESS_PHONE_DISPLAY': settings.BUSINESS_PHONE_DISPLAY,
        'BUSINESS_WHATSAPP': settings.BUSINESS_WHATSAPP,
        'BUSINESS_EMAIL': settings.BUSINESS_EMAIL,
        'GENERAL_WHATSAPP_LINK': f'https://wa.me/{settings.BUSINESS_WHATSAPP}?text={greeting}',
    }


def categories_menu(request):
    """Makes the category list available for the main navigation on every page."""
    return {
        'NAV_CATEGORIES': Category.objects.all(),
    }
