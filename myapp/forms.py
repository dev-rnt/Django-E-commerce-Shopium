from django import forms
from .models import *



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
        super(UserForm, self).__init__(*args, **kwargs)
        # self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        # self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        # self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        # self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    img = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['address_line_1','address_line_2','city','state','country','img']

    def __init__(self,*args,**kwargs):
        super(UserProfileForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
