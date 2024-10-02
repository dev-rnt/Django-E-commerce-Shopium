from django import forms
from .models import *
from django.core.exceptions import ValidationError



class EmailLoginForm(forms.Form):
    email = forms.EmailField(max_length=254,label='',label_suffix='', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))



class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,  # Ensure exactly 6 digits
        label='',  # No label text
        label_suffix='',  # No suffix
        required=True,
        help_text="Enter the 6-digit OTP sent to your email",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your OTP',
                'maxlength': '6',  # Limit input to 6 characters
                'pattern': r'\d{6}',  # Regex pattern for 6 digits
                'oninput': 'this.value=this.value.replace(/[^0-9]/g,"");'  # Remove non-numeric input
            }
        )
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        
        # Check if the OTP contains only digits
        if not otp.isdigit():
            raise ValidationError("OTP must contain only digits.")
        
        return otp


class PasswordForm(forms.Form):
     password = forms.CharField(label='', label_suffix=' ', min_length=6,required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}))


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name','email','subject','message']


class UpdateRevForm(forms.ModelForm):
    review = forms.CharField(label='Review',label_suffix='', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Review'}))
    rating = forms.FloatField(label='Rating', label_suffix='',required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Rating'}))

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if rating < 0.0 or rating > 5.0:
            raise forms.ValidationError('Rating should be between 0.0 and 5.0.')
        return rating

    class Meta:
        model = ReviewRating
        fields = ['review', 'rating','img1','img2','img3','img4','img5']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['review', 'rating','img1','img2','img3','img4','img5']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','phone','email','address_line_1','address_line_2',
        'country','state','city','order_note',]
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

class Registration(forms.ModelForm):
    first_name = forms.CharField(label='First name', label_suffix=' ', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}))
    last_name = forms.CharField(label='Last name', label_suffix=' ', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}))
    email = forms.CharField(label='Email', label_suffix=' ',help_text="We'll never share your personal info", required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}))
    phone_number = PhoneNumberField( label="Phone number",label_suffix=' ',widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact'}))
    password = forms.CharField(label='Password', label_suffix=' ', min_length=6,required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}))
    password2 = forms.CharField(label='Confirm Password', min_length=6,label_suffix=' ', required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = Account
        fields = ['first_name','last_name', 'email', 'phone_number', 'password','password2']

            # Override the save method to handle UserProfile's img field
    def save(self, commit=True):
        account = super().save(commit)

        # You can access the uploaded image using self.cleaned_data['img']
        img = self.cleaned_data.get('img')

        # Check if an image was provided before creating a UserProfile
        if img:
            UserProfile.objects.create(user=account, img=img)

        return account


    def clean(self):
        cd = super().clean()
        pas1 = cd.get('password')
        pas2 = cd.get('password2')
        if pas1!=pas2:
            raise forms.ValidationError("Passwords don't match")




class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


# class UserDetailsForm(forms.Form):
#     first_name = forms.CharField(max_length=50,label='',label_suffix='', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}))
#     last_name = forms.CharField(max_length=50, label='',label_suffix='',required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}))
#     phone_number = PhoneNumberField( label="",label_suffix=' ',widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact'}))


class UserDetailsForm(forms.Form):
    address_line_1 = forms.CharField(
        max_length=100,
        label="",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'})
    )
    
    address_line_2 = forms.CharField(
        max_length=100,
        label="",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2'})
    )
    
    city = forms.CharField(
        max_length=20,
        label="",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    
    state = forms.CharField(
        max_length=20,
        label="",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'})
    )
    
    country = forms.CharField(
        max_length=20,
        label="",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'})
    )



