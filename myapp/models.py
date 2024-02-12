from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager
from django.urls import reverse
from django.db.models import Avg , Count
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class Contact(models.Model):
    name = models.CharField(max_length=40,blank=False)
    email = models.EmailField(max_length=50,blank=False)
    subject = models.CharField(max_length=400)
    message = models.TextField(max_length=500)


class category(models.Model):
    category_name = models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    description = models.TextField(max_length=255,blank=True)
    cat_image = models.ImageField(upload_to='photos/categories',blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category',args=[self.slug])

    def __str__(self):
        return self.category_name


class MyAccountManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have an username')

        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
           email = self.normalize_email(email),
           username = username,
           first_name = first_name,
           last_name = last_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,first_name,last_name,email,username,password):
        user = self.create_user(
         email = self.normalize_email(email),
         username = username,
         password = password,
         first_name = first_name,
         last_name = last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)


#Overridding User Model
class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=100,unique=True)
    phone_number = PhoneNumberField()
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']

    objects = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self,perm,obj=None):
        return self.is_admin

    def has_module_perms(self,add_label):
        return True

    def __str__(self):
        return str(self.phone_number)

class UserProfile(models.Model):
    user = models.OneToOneField(Account,on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=100,blank=True)
    address_line_2 = models.CharField(max_length=100,blank=True)
    img = models.ImageField(blank=True,upload_to='userprofile/')
    city = models.CharField(blank=True,max_length=20)
    state = models.CharField(blank=True,max_length=20)
    country = models.CharField(blank=True,max_length=20)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'



class Product(models.Model):
    name = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=255)
    description = models.TextField(max_length=500,blank=True)
    brand = models.CharField(max_length=50,blank=True,default="Null")
    price = models.IntegerField()
    sprice = models.IntegerField(default=0,null=True,blank=True)
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(category,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])

    def __str__(self):
        return self.name

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count



class AvailableOffers(models.Model):
    prod_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    of1 = models.CharField(max_length=200,blank=True,null=True)
    of2 = models.CharField(max_length=200,blank=True,null=True)
    of3 = models.CharField(max_length=200,blank=True,null=True)
    of4 = models.CharField(max_length=200,blank=True,null=True)
    of5 = models.CharField(max_length=200,blank=True,null=True)




class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_cat='color',is_active=True)

    def sizes(self):
        return super(VariationManager,self).filter(variation_cat='size',is_active=True)




variation_cat_choice = (
   ('color','color'),
   ('size','size'),
)



class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_cat = models.CharField(max_length=100,choices=variation_cat_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = VariationManager()

    def __str__(self):
        return str(self.variation_value)
    # def __str__(self):
    #     return str(self.product)




class Cart(models.Model):
    cart_id = models.CharField(max_length=255,blank=True)
    data_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItems(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    product   = models.ForeignKey(Product,on_delete=models.CASCADE)
    cart      = models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    variation = models.ManyToManyField(Variation,blank=True)
    quantity  = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.sprice * self.quantity

    def __str__(self):
        return str(self.product)



class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100) # this is the total amount paid
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return self.product.product_name




class ReviewRating(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    review = models.TextField(max_length=500,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20,blank=True)
    img1 = models.ImageField(upload_to='reviewimages',blank=True,null=True)
    img2 = models.ImageField(upload_to='reviewimages',blank=True,null=True)
    img3 = models.ImageField(upload_to='reviewimages',blank=True,null=True)
    img4 = models.ImageField(upload_to='reviewimages',blank=True,null=True)
    img5 = models.ImageField(upload_to='reviewimages',blank=True,null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # def __str__(self):
    #     return self.subject



class ProductGallery(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    img = models.ImageField(upload_to='productgallery',max_length=50)

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'Product Gallery'
