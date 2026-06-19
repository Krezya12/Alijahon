from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import *
from django.utils import timezone


class CustomUserManager(UserManager):

    def _create_user_object(self, phone_number, password, **extra_fields):

        user = self.model(phone_number=phone_number, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, phone_number, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        user = self._create_user_object(phone_number, password, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)


class Region(Model):
    title = CharField(max_length=12)


class City(Model):
    title = CharField(max_length=12)
    region = ForeignKey('Region', on_delete=CASCADE, related_name='cities')


class User(AbstractUser):
    class RoleType(TextChoices):
        admin = 'admin', 'Admin'
        deliver = 'deliver', 'Deliver'

    username = None
    first_name = CharField(max_length=12, blank=True, null=True)
    last_name = CharField(max_length=12, blank=True, null=True)
    phone_number = CharField(max_length=19, unique=True)
    city = ForeignKey('City', on_delete=CASCADE, related_name='users', null=True, blank=True)
    tg_id = IntegerField(default=0, blank=True, null=True)
    description = TextField(default='', blank=True, null=True)
    api_key = CharField(max_length=11, default='')
    balance = DecimalField(decimal_places=2, max_digits=12, default=0)
    on_way = DecimalField(decimal_places=2, max_digits=12, default=0)
    role = CharField(choices=RoleType, default='')

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


class Category(Model):
    title = CharField(max_length=12)
    logo = CharField(max_length=255)


class Product(Model):
    title = CharField(max_length=12)
    description = TextField()
    quantity = IntegerField()
    category = ForeignKey('Category', on_delete=CASCADE, related_name='products')
    price = DecimalField(decimal_places=2, max_digits=12)
    payment = DecimalField(decimal_places=2, max_digits=12, default=0)
    created_at = DateTimeField(auto_now_add=True)


class Image(Model):
    image = ImageField(upload_to='product/images/')
    product = ForeignKey('Product', on_delete=CASCADE, related_name='images')


class Flow(Model):
    title = CharField(max_length=12)
    discount = DecimalField(decimal_places=2, max_digits=12, default=0)
    user = ForeignKey('User', on_delete=CASCADE, related_name='flows')
    product = ForeignKey('Product', on_delete=CASCADE, related_name='flows')
    visits = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)


class Order(Model):
    class StatusType(TextChoices):
        PACKING = 'packing', 'Packing'
        DELIVERING = 'delivering', 'Delivering'
        DELIVERED = 'delivered', 'Delivered'
        POSTPONED = 'postponed', 'Postponed'
        RETURNED = 'returned', 'Returned'
        CANCELLED = 'cancelled', 'Cancelled'
        HOLD = 'hold', 'Hold'
        ARCHIVE = 'archive', 'Archive'
        READY = 'ready', 'Ready'


    status = CharField(choices=StatusType, default=StatusType.PACKING)

    flow = ForeignKey('Flow', on_delete=CASCADE, related_name='orders', blank=True, null=True)
    product = ForeignKey('Product', on_delete=CASCADE, related_name='orders', blank=True, null=True)
    city = ForeignKey('City', on_delete=CASCADE, related_name='orders', blank=True, null=True)

    phone_number = CharField(max_length=19, default='', blank=True, null=True)
    full_name = CharField(max_length=255, default='', blank=True, null=True)
    quantity = IntegerField(default=1)
    comment = CharField(max_length=255, default='')

    created_at = DateTimeField(default=timezone.now)
    last_modified = DateTimeField(auto_now=True)
    delivery_date = DateTimeField(null=True, blank=True)


class Transaction(Model):
    class StatusType(TextChoices):
        SUCCESS = 'success', 'Success'
        ON_WAY = 'on_way', 'On Way'
        CANCELLED = 'cancelled', 'Cancelled'


    user = ForeignKey('User', on_delete=CASCADE, related_name='banks')

    account_number = IntegerField()
    amount = DecimalField(decimal_places=2, max_digits=12, default=0)
    status = TextField(choices=StatusType, default=StatusType.ON_WAY)
    sms = CharField(max_length=1219, default='')

    created_at = DateTimeField(auto_now_add=True)


class Favorite(Model):
    user = ForeignKey('User', on_delete=CASCADE, related_name='favorites')
    product = ForeignKey('Product', on_delete=CASCADE, related_name='favorites')

    created_at = DateTimeField(auto_now_add=True)
