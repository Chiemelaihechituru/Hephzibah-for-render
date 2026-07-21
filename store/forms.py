from django import forms

from .models import Order, WholesaleEnquiry


class OrderForm(forms.ModelForm):
    """Collected on a product page before we hand the customer off to WhatsApp."""

    quantity = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = Order
        fields = ['customer_name', 'phone_number', 'address', 'note']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'placeholder': 'Your full name',
                'autocomplete': 'name',
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'e.g. 0801 234 5678',
                'autocomplete': 'tel',
                'inputmode': 'tel',
            }),
            'address': forms.Textarea(attrs={
                'placeholder': 'Delivery address',
                'rows': 3,
            }),
            'note': forms.Textarea(attrs={
                'placeholder': 'Anything else we should know? (size, colour, etc.) — optional',
                'rows': 2,
            }),
        }
        labels = {
            'customer_name': 'Full name',
            'phone_number': 'Phone number',
            'address': 'Delivery address',
            'note': 'Note (optional)',
        }


class WholesaleEnquiryForm(forms.ModelForm):
    class Meta:
        model = WholesaleEnquiry
        fields = [
            'business_name', 'contact_name', 'location', 'phone_number',
            'email', 'estimated_monthly_quantity', 'message',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'placeholder': 'e.g. Grace Boutique'}),
            'contact_name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'location': forms.TextInput(attrs={'placeholder': 'City / State'}),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'e.g. 0801 234 5678', 'inputmode': 'tel',
            }),
            'email': forms.EmailInput(attrs={'placeholder': 'you@business.com (optional)'}),
            'estimated_monthly_quantity': forms.TextInput(attrs={
                'placeholder': 'e.g. 50-100 pieces a month',
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Tell us a bit about your business — optional',
                'rows': 3,
            }),
        }
        labels = {
            'business_name': 'Business name',
            'contact_name': 'Your name',
            'location': 'Location',
            'phone_number': 'Phone number',
            'estimated_monthly_quantity': 'Estimated monthly order quantity',
        }
