from django.contrib import admin
from .models import *
from django.utils.html import format_html
import admin_thumbnails


# Register your models here.
@admin.register(Contact)
class ContactAmin(admin.ModelAdmin):
    list_display = ['name','email','subject','message']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user','address_line_1','address_line_2','img','city','state','country', 'thumbnail']

    def thumbnail(self, obj):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(obj.img.url))
    thumbnail.short_description = 'Thumbnail'

@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'review', 'rating', 'ip', 'status','img1','img2','img3','img4','img5','created_at', 'updated_at']

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    readonly_fields = ['password','is_admin','is_active','is_staff','is_superadmin']
    search_fields = ['first_name','last_name']
    list_display_links = ['email','first_name','last_name']
    list_display = ['id','first_name','last_name','email','phone_number','date_joined','last_login','is_active']

@admin.register(Payment)
class PaymentModel(admin.ModelAdmin):
    search_fields = ['user']
    list_display = ['user','payment_id','payment_method','amount_paid','status','created_at']


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ['id','order','payment','user','product','variation','quantity','product_price','ordered']
    extra = 0

    def has_delete_permission(self, request, obj=None):
        # Disable delete permission
        return False


@admin.register(Order)
class Order(admin.ModelAdmin):
    search_fields = ['user','first_name','last_name']
    list_display = ['user','payment','order_number','first_name','last_name','phone','email','address_line_1','address_line_2',
    'country','state','city','order_note','order_total','tax','status','ip','is_ordered','created_at','updated_at']
    list_filter = ['status','is_ordered']
    list_per_page = 10
    inlines = [OrderProductInline]

@admin.register(OrderProduct)
class OrderProduct(admin.ModelAdmin):
    search_fields = ['user','first_name','last_name']
    list_display = ['order','payment','user','product','display_mtmf','quantity','product_price','ordered','created_at','updated_at']

    def display_mtmf(self, obj):
        return ', '.join(str(item) for item in obj.variation.all())
    display_mtmf.short_description = 'ManyToManyField'

@admin.register(category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('category_name',)}
    list_display = ['id','category_name','slug','description','cat_image']


@admin_thumbnails.thumbnail('img')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 0
    list_display_links = ['img']

class AvailableOffersGalleryInline(admin.TabularInline):
    model = AvailableOffers
    extra = 0

class VariationAdmin(admin.TabularInline):
    model = Variation
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
    list_editable = ['stock']
    list_display = ['id','slug','name','description','price','sprice','images','thumbnail','stock','is_available','category','created_at','modified_date']
    inlines = [ProductGalleryInline,AvailableOffersGalleryInline,VariationAdmin]

    def thumbnail(self, obj):
        return format_html('<img src="{}" width="30" style="border-radius:80%;">'.format(obj.images.url))
    thumbnail.short_description = 'Images'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','cart_id','data_added']

@admin.register(CartItems)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ['id','product','cart','display_mtmf','quantity','is_active']
    def display_mtmf(self, obj):
        return ', '.join(str(item) for item in obj.variation.all())
    display_mtmf.short_description = 'ManyToManyField'

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ['id','product','variation_cat','variation_value','is_active','created_at']
    search_fields = ['product']
    list_editable = ('is_active','variation_cat','variation_value')
    list_filter = ['product','variation_cat','variation_value']

@admin.register(AvailableOffers)
class AvailableOffersAdmin(admin.ModelAdmin):
    list_display = ['prod_id','of1','of2','of3','of4','of5']


@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ['id','img','product']
