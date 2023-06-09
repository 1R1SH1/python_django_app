from django import forms
# from django.core import validators
from django.contrib.auth.models import Group

from shopapp.models import Product, Order


# class ProductForm(forms.Form):
#     name = forms.CharField(max_length=100)
#     price = forms.DecimalField(min_value=1, max_value=1000000, decimal_places=2)
#     description = forms.CharField(
#         label='Product description',
#         widget=forms.Textarea(attrs={'rows': 5, 'cols': '30'}),
#         validators=[validators.RegexValidator(
#             regex=r'great',
#             message='Field must contain word "greate"'
#         )]
#     )


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = 'name', 'price', 'created_by', 'description', 'discount'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = 'delivery_address', 'promocods', 'user', 'products'
