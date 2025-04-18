# shop/forms.py
from django import forms

class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=100, label='Имя')
    address = forms.CharField(max_length=255, label='Адрес')
    phone = forms.CharField(max_length=20, label='Телефон')
