import re
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.db.models import F
from django.forms import ModelForm, CharField, Form

from apps.models import User, Flow, Product, Transaction, Favorite, Order


class UserModelForm(ModelForm):
    confirm_password = CharField(max_length=50)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'confirm_password']

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 3:
            raise ValidationError('Password uzunligi yetarli emas')
        hash_password = make_password(password)
        return hash_password

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        phone_number = re.sub(r'\D', "", phone_number)
        return phone_number

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data['confirm_password']
        password = self.data['password']
        if confirm_password != password:
            raise ValidationError('Confirm password xato')


class LoginModelForm(Form):
    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = request

    phone_number = CharField(max_length=19)
    password = CharField(max_length=128)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        phone_number = re.sub(r'\D', "", phone_number)

        queryset = User.objects.filter(phone_number=phone_number)

        if not queryset.exists():
            raise ValidationError('Bunday nomer yoq!')

        return phone_number

    def clean_password(self):
        password = self.cleaned_data['password']

        print(self.cleaned_data['phone_number'])

        queryset = User.objects.filter(phone_number=self.cleaned_data['phone_number'])
        if queryset.exists():
            user = queryset.first()
            if check_password(password, user.password):
                login(self.request, user)
            else:
                raise ValidationError('Parol xato!')


8


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'description', 'tg_id', 'city']


class LogoutForm(Form):
    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = request

    def logout(self):
        logout(self.request)


class FlowModelForm(ModelForm):
    class Meta:
        model = Flow
        fields = ['title', 'discount', 'user', 'product']

    def clean_discount(self):
        discount = self.cleaned_data['discount']
        product = Product.objects.filter(id=int(self.data['product'])).first()

        discount = product.price - discount

        if discount < product.payment:
            raise ValidationError('Chegirma tolovdan katta bolishi mumkin emas!')
        return discount


class TransactionModelForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['user', 'account_number', 'amount', 'sms']

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        User.objects.filter(pk=int(self.data['user'])).update(balance=F('balance') - amount)

        return amount


#
# class ViewsModelForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ['views']


class FavModelForm(ModelForm):
    class Meta:
        model = Favorite
        fields = ['user', 'product']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')

        if self.user and product:
            favorite_qs = Favorite.objects.filter(user=self.user, product=product)

            if favorite_qs.exists():
                favorite_qs.delete()
                self.is_removed_action = True
                raise ValidationError("Товар успешно удален из избранного.")

        return cleaned_data


class OrderModelForm(ModelForm):
    class Meta:
        model = Order
        fields = ['quantity', 'flow', 'full_name', 'phone_number', 'product', 'comment', 'status', 'delivery_date', 'city']

