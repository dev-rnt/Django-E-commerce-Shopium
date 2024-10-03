from django.shortcuts import render , redirect
from .models import *
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.shortcuts import HttpResponse
from django.core.exceptions import ValidationError
from .forms import Registration
from django.contrib import messages , auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from .models import Account

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
import requests
import datetime
from .forms import *
import json
from django.conf import settings


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle




def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        reg = Contact(name=name,email=email,subject=subject,message=message)
        reg.save()
        messages.info(request,'Your form was submitted successfully!')
    return render(request,'myapp/contact.html')

def updaterev(request, user_id):
    next_url = request.GET.get('next', '/')
    try:
        data = ReviewRating.objects.get(id=user_id)
    except ReviewRating.DoesNotExist:
        return redirect(next_url)

    product = data.product
    user = request.user
    ip = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        form = UpdateRevForm(request.POST, request.FILES, instance=data)

        if form.is_valid():
            img1 = request.FILES.get('img1')
            img2 = request.FILES.get('img2')
            img3 = request.FILES.get('img3')
            img4 = request.FILES.get('img4')
            img5 = request.FILES.get('img5')
            form.img1 = img1
            form.img2 = img2
            form.img3 = img3
            form.img4 = img4
            form.img5 = img5
            form.save()
            referer = next_url
            url_with_anchor = f"{referer}?scroll_to=comments"
            return redirect(url_with_anchor)


    else:
        form = UpdateRevForm(instance=data)

    return render(request, 'myapp/updaterev.html', {'form': form,'r':data})

def deleterev(request, user_id):
    data = ReviewRating.objects.get(id=user_id)
    data.delete()

    messages.info(request, "Your review has been deleted. Thank you.")

    # Get the URL of the previous page and append the anchor as a query parameter
    referer = request.META.get('HTTP_REFERER', '/')
    url_with_anchor = f"{referer}?scroll_to=comments"

    return redirect(url_with_anchor)

def submtreview(request, product_id):
    url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)  
        if form.is_valid():
            data = form.save(commit=False)
            uploaded_files = request.FILES.getlist('images')

            # Loop through the first 5 files and assign them to the corresponding fields
            for i in range(min(len(uploaded_files), 5)):
                field_name = f'img{i + 1}' 
                setattr(data, field_name, uploaded_files[i])
            data.product_id = product_id
            data.user_id = request.user.id
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            messages.success(request, 'Thank you! Your review has been submitted.')
            referer = request.META.get('HTTP_REFERER', '/')
            url_with_anchor = f"{referer}?scroll_to=comments"
            return redirect(url_with_anchor)

def generatepdf(request,order_number=None,transID=None):
    if order_number and transID:
            order_number = order_number
            transID = transID

            try:
                order = Order.objects.get(order_number=order_number,is_ordered=True)
                ordered_products = OrderProduct.objects.filter(order_id=order.id)
                payment = Payment.objects.get(payment_id=transID)
                subtotal = 0
                for i in ordered_products:
                    subtotal += i.product_price * i.quantity
            except:
                pass



            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'filename=order_{order.order_number}.pdf'

            # Create a canvas to draw on the PDF
            p = canvas.Canvas(response, pagesize=letter)

            # Define page size
            width, height = letter

            # Add a header with a heading

            # Draw a black line below the heading spanning the full width
            p.setLineWidth(1)  # Set the line widthS
            p.setStrokeColorRGB(0, 0, 0)  # Set the line color to black
            p.line(0, height - 60, width, height - 60)  # Draw the line across the full width

            # Draw the text "Shop" in orange
            p.setFillColorRGB(255/255, 153/255, 0/255)
            p.setFont("Helvetica-Bold", 33)
            p.drawCentredString(256, 750, "Shop")

            # Draw the text "eum" in grey
            p.setFillColorRGB(128/255, 128/255, 128/255)
            p.setFont("Helvetica-Bold", 33)
            p.drawCentredString(330, 750, "eum")



            # p.drawInlineImage('static/myapp/images/Untitled.png', 130, 400)
            p.setFillColorRGB(0,0,0)
            p.setFont("Helvetica-Bold", 16)
            # Write order details to the PDF
            p.drawString(430, 700, f'Invoiced To')

            p.setFillColorRGB(64/255, 64/255, 64/255)


            p.setFont("Helvetica-Bold", 10)
            p.drawString(430, 680, f'Name:{order.first_name} {order.last_name}')
            p.drawString(430, 670, f'Address:{order.address_line_1} ')
            p.drawString(430, 660, f'City:{order.city},State:{order.state}')
            p.drawString(430, 650, f'Country:{order.country}')

            p.setFont("Helvetica-Bold", 13)
            p.drawString(40, 700, f'Order Number: {order.order_number}')
            p.drawString(40, 680, f'Transaction ID: {payment.payment_id}')

            order_date = order.created_at

            # Format the date as "Jan. 24, 2024, 9:34 p.m."
            formatted_date = order_date.strftime('%b. %d, %Y, %I:%M %p')

            # Draw the formatted date
            p.drawString(40, 660, f'Order Date: {formatted_date}')

            p.drawString(40, 640, f'Status: {payment.status}')

            # Add more details as needed

            # Draw a table for ordered products
            table_data = [['Product', 'Color & Size', 'Quantity', 'Price', 'Total']]

            for order_product in ordered_products:
                product_name = order_product.product.name
                variations = ', '.join([variation.variation_value for variation in order_product.variation.all()])
                quantity = str(order_product.quantity)
                price_per_unit = f'Rs {order_product.product_price}'
                total_price = f'{order_product.product_price * order_product.quantity} Rs'

                table_data.append([f'{product_name}', f'{variations}', quantity, price_per_unit, total_price])


            table = Table(table_data)
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                       ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                       ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                       ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                       ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                       ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                       ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                       ('FONTSIZE', (0, 0), (-1, -1), 12)]))

            table.wrapOn(p, width, height)
            table.drawOn(p, 30, 500)
            # p.showPage()
            # p.save()

            table_data = [['Sub Total', 'Tax', 'Grand Total']]

            table_data.append([
                        str(f'Rs {subtotal}'),
                        str(f'Rs {order.tax}'),
                        str(f'Rs {order.order_total}'),
            ])

            table = Table(table_data)
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                       ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                       ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                       ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                       ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                       ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                       ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                       ('FONTSIZE', (0, 0), (-1, -1), 12)]))

            table.wrapOn(p, width, height)
            table.drawOn(p, 373, 440)

            # Draw a black line below the heading spanning the full width
            line_position = height - 400  # Adjust this value to change the line position

            p.setLineWidth(1)  # Set the line width
            p.setStrokeColorRGB(0, 0, 0)  # Set the line color to black
            p.line(0, line_position, width, line_position)  # Draw the line across the full width


            p.setFillColorRGB(64/255, 64/255, 64/255)  # Dark grey color
            p.setFont("Helvetica-Bold", 20)
            p.drawCentredString(300, 360, "Thank you for shopping with us.")

            p.showPage()
            p.save()
            return response


def order_completed(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product.sprice * i.quantity


        context = {
           'order':order,
           'ordered_products':ordered_products,
           'order_number':order.order_number,
           'transID':payment.payment_id,
           'payment':payment,
           'sub_total':subtotal,
           'order_number':order_number,
           'transID':transID,
        }
        return render(request,'myapp/order_complete.html',context)
    except (Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('Home')




def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])

    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    #Move the cart items to Order Product Table
    cart_items = CartItems.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.sprice
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItems.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()


        #Reduce the quantity of from original product
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()


    #clear cart
    CartItems.objects.filter(user=request.user).delete()


    #send email ordered to customer

    mail_subject = 'Thank you for your order!'
    message = render_to_string('myapp/order_received.html',{
        'user':request.user,
        'order':order,
    })
    to_email = request.user.email
    send_email = EmailMultiAlternatives(mail_subject,message,to=[to_email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()

    data = {
        'order_number':order.order_number,
        'transID':payment.payment_id
        }
    return JsonResponse(data)
    # return render(request,'myapp/payments.html')



def order(request,total=0, quantity=0):
    user = request.user
    #if cart item not found redirect to shop
    cart_items = CartItems.objects.filter(user=user)
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('Store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.sprice * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            #Generate Order Number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            currentdate = d.strftime("%Y%m%d")
            order_number = currentdate + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=user,is_ordered=False,order_number=order_number)
            context = {
            'order':order,
            'cart_items':cart_items,
            'total':total,
            'tax':tax,
            'grand_total':grand_total
            }
            return render(request,'myapp/payments.html',context)
    else:
        return redirect('Checkout')

def register(request):
    if request.method == 'POST':
        form = Registration(request.POST,request.FILES)
        if form.is_valid():
            fn = form.cleaned_data['first_name']
            ls = form.cleaned_data['last_name']
            e = form.cleaned_data['email']
            c = form.cleaned_data['phone_number']
            p = form.cleaned_data['password']
            i = request.FILES.get('img')
            username = e.split("@")[0]
            user = Account.objects.create_user(first_name=fn,last_name=ls,email=e,password=p,username=username)
            userpic = UserProfile(user=user,img=i)
            userpic.save()
            user.phone_number=c
            user.save()

            #User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('myapp/accountver.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = e
            send_email = EmailMultiAlternatives(mail_subject,message,to=[to_email])
            send_email.attach_alternative(message, "text/html")
            send_email.send()
            # messages.success(request,'Your account is created.')
            return redirect('/accounts/login/?command=verification&email='+e)
    else:
        form = Registration()
    context ={'form':form}
    return render(request,'myapp/register.html',context)






def login_form(request):
    if request.method == 'POST':
        email = request.POST['email']
        passw = request.POST['password']
        user = auth.authenticate(email=email,password=passw)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItems.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItems.objects.filter(cart=cart)

                    #Getting Production variation
                    list1 = []
                    for item in cart_item:
                        variation = item.variation.all()
                        list1.append(list(variation))

                    #get the cart items to access
                    cart_items = CartItems.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_items:
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in list1:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItems.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItems.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass
            auth.login(request,user)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)

            except:
                  return redirect('Dashboard')

        else:
            
            messages.error(request,'Invalid login credentials please try again')
            return redirect('Login')      
    return render(request,'myapp/login.html')




@login_required(login_url='Login')
def logout(request):
    auth.logout(request)
    messages.info(request,'You are logged out')
    return redirect('Login')


def home(request):
    products = Product.objects.filter(is_available=True)[:8]
    latest_products = Product.objects.filter(is_available=True).order_by('-created_at')[:4]

    product_discounts = [] 

    for product in products:
        original_price = product.price
        selling_price = product.sprice

        def calculate_percentage_discount(original_price, selling_price):
            if original_price == 0:
                return 0  # Handle the case where the original price is zero to avoid division by zero

            percentage_discount = ((original_price - selling_price) / original_price) * 100
            return round(percentage_discount, 2)  # Round to two decimal places

        percentage_discount = round(calculate_percentage_discount(original_price, selling_price))

        product_discounts.append((product, percentage_discount))

    latest_product_discounts = []  # List to store tuples of (product, discount)

    # Calculate discounts for latest products
    for product in latest_products:
        original_price = product.price
        selling_price = product.sprice

        def calculate_percentage_discount(original_price, selling_price):
            if original_price == 0:
                return 0  # Handle the case where the original price is zero to avoid division by zero

            percentage_discount = ((original_price - selling_price) / original_price) * 100
            return round(percentage_discount, 2)  # Round to two decimal places

        percentage_discount = round(calculate_percentage_discount(original_price, selling_price))

        latest_product_discounts.append((product, percentage_discount))

    context = {
        'product_discounts': product_discounts,
        'latest_product_discounts': latest_product_discounts
    }
    return render(request, 'myapp/index.html', context)


def store(request, category_slug=None):
    size = request.GET.get('size')
    price = request.GET.get('price')
    price2 = request.GET.get('price2')

    if category_slug is not None:
        cat = get_object_or_404(category, slug=category_slug)
        data = Product.objects.filter(category=cat, is_available=True).order_by('id')
    else:
        data = Product.objects.filter(is_available=True).order_by('-created_at')

    # Apply size filter
    if size:
        data = data.filter(variation__variation_value=size)

    # Apply price filter
    if price is not None and price2 is not None:
        data = data.filter(sprice__gte=price, sprice__lte=price2)

    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    page_products = paginator.get_page(page)
    data1 = data.count()

    context = {'data': page_products, 'data1': data1}
    return render(request, 'myapp/store.html', context)

def product_detail(request,category_slug,product_slug):
    try:
        data = Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = CartItems.objects.filter(cart__cart_id=_cart_id(request),product=data).exists()
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user,product_id=data.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None


    reviews = ReviewRating.objects.filter(product_id=data.id,status=True).order_by('-created_at')
    average_rating = ReviewRating.objects.filter(product_id=data.id,status=True).aggregate(Avg('rating'))['rating__avg']
    original_price = data.price
    selling_price = data.sprice

    def calculate_percentage_discount(original_price, selling_price):
        if original_price == 0:
            return 0  # Handle the case where the original price is zero to avoid division by zero

        percentage_discount = ((original_price - selling_price) / original_price) * 100
        return round(percentage_discount, 2)  # Round to two decimal places

    percentage_discount = calculate_percentage_discount(original_price, selling_price)
    product_gallery = ProductGallery.objects.filter(product_id=data.id)
    aval_offer = AvailableOffers.objects.filter(prod_id=data)
    context = {
    'data':data,
    'in_cart':in_cart,
    'orderproduct':orderproduct,
    'reviews':reviews,
    'product_gallery':product_gallery,
    'average_rating':average_rating,
    'percentage_discount':percentage_discount,
    'aval_offer':aval_offer
    }
    return render(request,'myapp/product-detail.html',context)



def add_cart(request,product_id):
    current_user = request.user
    data = Product.objects.get(pk=product_id)
    if current_user.is_authenticated:
        list1 = []
        if request.method == 'POST':
            for key,value in request.POST.items():
                try:
                    prod = Variation.objects.get(product=data,variation_cat__iexact=key,variation_value__iexact=value)
                    list1.append(prod)
                except:
                    pass



        is_cart_item_exists = CartItems.objects.filter(product=data,user=current_user).exists()
        if is_cart_item_exists:
            cart_items = CartItems.objects.filter(product=data,user=current_user)
            ex_var_list = []
            id = []
            for item in cart_items:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)


            if list1 in ex_var_list:
                index = ex_var_list.index(list1)
                item_id = id[index]
                item = CartItems.objects.get(product=data,id=item_id)
                item.quantity +=1
                item.save()


            else:
                item = CartItems.objects.create(product=data, quantity=1, user=current_user)
                if len(list1) > 0:
                    item.variation.clear()
                    item.variation.add(*list1)
                item.save()



        else:
            cart_items = CartItems.objects.create(
            product = data,
            quantity = 1,
            user = current_user,
            )
            if len(list1) > 0:
                cart_items.variation.clear()
                # cart_items.variation.add(*list1)
                for item in list1:
                    cart_items.variation.add(item)
            cart_items.save()
        return redirect('/cart/')

    else:

        list1 = []
        if request.method == 'POST':
            for key,value in request.POST.items():
                try:
                    prod = Variation.objects.get(product=data,variation_cat__iexact=key,variation_value__iexact=value)
                    list1.append(prod)
                except:
                    pass
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
            cart_id = _cart_id(request)
            )
        cart.save()


        is_cart_item_exists = CartItems.objects.filter(product=data,cart=cart).exists()
        if is_cart_item_exists:
            cart_items = CartItems.objects.filter(product=data,cart=cart)
            ex_var_list = []
            id = []
            for item in cart_items:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            if list1 in ex_var_list:
                index = ex_var_list.index(list1)
                item_id = id[index]
                item = CartItems.objects.get(product=data,id=item_id)
                item.quantity +=1
                item.save()
            else:
                item = CartItems.objects.create(product=data, quantity=1, cart=cart)
                if len(list1) > 0:
                    item.variation.clear()
                    item.variation.add(*list1)
                item.save()
        else:
            cart_items = CartItems.objects.create(
            product = data,
            quantity = 1,
            cart = cart,
            )
            if len(list1) > 0:
                cart_items.variation.clear()
                for item in list1:
                    cart_items.variation.add(item)
            cart_items.save()
        return redirect('/cart/')


def remove_cart(request,product_id,cart_item):
    product = get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItems.objects.get(product=product,user=request.user,id=cart_item)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItems.objects.get(product=product,cart=cart,id=cart_item)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('/cart/')



def remove_cart_item(request,product_id,cart_item):
    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItems.objects.get(product=product,user=request.user,id=cart_item)

    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItems.objects.get(product=product,cart=cart,id=cart_item)
    cart_item.delete()
    return redirect('/cart/')



def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax= 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItems.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItems.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+= (cart_item.product.sprice*cart_item.quantity)
            quantity+=cart_item.quantity
        tax = (2*total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass
    context = {
    'total':total,
    'quantity':quantity,
    'cart_items':cart_items,
    'tax':tax,
    'grand_total':grand_total
    }
    return render(request,'myapp/cart.html',context)

def search(request):
    data = None
    data1=0
    if 'keyword' in request.GET:
        key = request.GET['keyword']
        if key:
            data = Product.objects.order_by('-created_at').filter(description__icontains=key) | Product.objects.filter(name__icontains=key)
            data1 = data.count()


    context = {'data': data,'data1':data1,'key':key}
    return render(request, 'myapp/store.html', context)



def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations! Your account is activated.')
        return redirect('Login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('Register')




@login_required(login_url='Login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count = orders.count()
    try:
       userprofile = UserProfile.objects.get(user_id=request.user.id)
    except:
        userprofile = None   
    context = {
    'orders_count':orders_count,
    'userprofile':userprofile
    }
    return render(request,'myapp/dashboard.html',context)



def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            #User Forgot Activation
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('myapp/resetver.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMultiAlternatives(mail_subject,message,to=[to_email])
            send_email.attach_alternative(message, "text/html")
            send_email.send()

            messages.success(request,'Password reset email has been sent to your email address')
            return redirect('Login')
        else:
            messages.error(request,'Account Does not exist!')
            return redirect('ForgotPassword')
    return render(request,'myapp/forgotpassword.html')


def resetpassword(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your password')
        return redirect('PasswordReset')
    else:
        messages.error(request,'This link has been expired!')
        return redirect('Login')


def passwordReset(request):
    if request.method == 'POST':
        password = request.POST['password']
        password1 = request.POST['password1']

        if password == password1:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successful')
            return redirect('Login')

        else:
            messages.error(request,'Password do not match!')
            return redirect('PasswordReset')
    else:
        return render(request,'myapp/passwordreset.html')

@login_required(login_url='Login')
def checkout(request,total=0,quantity=0,cart_items=None):
    try:
        tax= 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItems.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItems.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total = (cart_item.product.sprice*cart_item.quantity)
            quantity+=cart_item.quantity
        tax = (2*total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass
    context = {
    'total':total,
    'quantity':quantity,
    'cart_items':cart_items,
    'tax':tax,
    'grand_total':grand_total
    }
    return render(request,'myapp/checkout.html',context)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def my_order(request):
    orders = Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context = {
    'orders':orders
    }
    return render(request,'myapp/my_order.html',context)








def editprofile(request):
    # Get or create the user profile for the logged-in user
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        pform = UserDetailsForm(request.POST, request.FILES)  # Include POST and FILES data

        if form.is_valid() and pform.is_valid():
            # Save the user form data
            form.save()

            # Save the user profile data
            userprofile.address_line_1 = pform.cleaned_data.get('address_line_1')
            userprofile.address_line_2 = pform.cleaned_data.get('address_line_2')
            userprofile.city = pform.cleaned_data.get('city')
            userprofile.state = pform.cleaned_data.get('state')
            userprofile.country = pform.cleaned_data.get('country')

            # Handle image upload if available
            if request.FILES.get('profile_image'):
                uploaded_image = request.FILES['profile_image']
                userprofile.img = uploaded_image

            userprofile.save()

            messages.success(request, 'Your profile has been updated.')
            return redirect('EditProfile')
    else:
        form = UserForm(instance=request.user)
        
        # Prepopulate the UserDetailsForm with existing data from the userprofile
        pform = UserDetailsForm(initial={
            'address_line_1': userprofile.address_line_1,
            'address_line_2': userprofile.address_line_2,
            'city': userprofile.city,
            'state': userprofile.state,
            'country': userprofile.country,
        })

    context = {
        'form': form,
        'pform': pform,
        'userprofile': userprofile,
    }

    return render(request, 'myapp/editprofile.html', context)

    
def changepass(request):
    if request.method == 'POST':
        curpass = request.POST['currpass']
        newpass = request.POST['newpass']
        newpass2 = request.POST['newpass2']

        user = Account.objects.get(username__exact=request.user.username)

        if newpass == newpass2:
            success = user.check_password(curpass)
            if success:
                user.set_password(newpass)
                user.save()
                auth.logout(request)
                messages.success(request,'Password updated successfully')
                return redirect('Login')
            else:
                messages.error(request,'Please enter a valid current password')
                return redirect('ChangePass')
        else:
            messages.error(request,'Password does not match!')
            return redirect('ChangePass')
    return render(request,'myapp/changepass.html')




def orderdetails(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    payment = order_detail.first().payment if order_detail.exists() else None
    subtotal = 0
    for i in order_detail:
        subtotal += i.product.sprice * i.quantity

    context = {
    'order_detail':order_detail,
    'order':order,
    'subtotal': subtotal,
    'payment':payment
    }


    return render(request,'myapp/orderdetails.html',context)



#OTP 
import random
from django.core.mail import send_mail

def generate_otp():
    return random.randint(100000, 999999)

def send_otp(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}'
    email_from = 'trash29172@gmail.com'  # Replace with your email
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def email_login_or_signup(request):
    # Step 1: Ask for email and send OTP
    if 'otp_verified' not in request.session:  # OTP not yet verified
        if request.method == 'POST':
            form = EmailLoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                request.session['email'] = email  # Store email in session for later use

                # Check if user exists
                if Account.objects.filter(email=email).exists():
                    request.session['existing_user'] = True  # Mark as existing user
                else:
                    request.session['existing_user'] = False  # Mark as new user

                # Generate and send OTP
                otp = generate_otp()
                request.session['otp'] = otp  # Store OTP in session for verification
                send_otp(email, otp)  # Send OTP to the provided email
                
                return redirect('verify_otp')  # Redirect to OTP verification page
        else:
            form = EmailLoginForm()

        return render(request, 'myapp/login.html', {'form': form})

    else:
        # Step 2: After OTP verification, handle the next steps (user creation or login)
        return redirect('verify_otp')  # Redirect to OTP verification page if OTP already sent


def ask_for_password(request):
    if request.method == 'POST':
        password_form = PasswordForm(request.POST)
        if password_form.is_valid():
            password = password_form.cleaned_data['password']
            email = request.session['email']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('Home')  # Redirect to home page after login
            else:
                # Add an error message for invalid password
                password_form.add_error(None, "Invalid password. Please try again.")
    else:
        password_form = PasswordForm()
    
    return render(request, 'myapp/password_prompt.html', {'form': password_form})





def verify_otp(request):
    if request.method == 'POST':
        otp_form = OTPForm(request.POST)
        if otp_form.is_valid():
            input_otp = otp_form.cleaned_data['otp']
            session_otp = request.session.get('otp')

            if session_otp is None:
                return redirect('email_login')

            if input_otp == str(session_otp):
                # OTP is correct, set session flag and redirect
                request.session['otp_verified'] = True

                # Clean unnecessary session data
                del request.session['otp']

                email = request.session.get('email', '')
                
                # For existing users, log them in
                if request.session.get('existing_user'):
                    user = Account.objects.get(email=email)
                    login(request, user)  # Log the user in

                    # Clean session data
                    del request.session['otp_verified']
                    del request.session['existing_user']

                    # Redirect to home page after successful login
                    return redirect('Home')
                else:
                    # Redirect to user details form for new user
                    return redirect('user_details_form')
            else:
                # Invalid OTP, retry OTP verification
                messages.error(request, 'Invalid OTP, please try again.')
                return redirect('verify_otp')
    
    else:
        otp_form = OTPForm()

    # Display the OTP verification form
    email = request.session.get('email', '')  # Get email from session if available
    return render(request, 'myapp/verifyotp.html', {'form': otp_form, 'email': email})







def user_details_form(request):
    if not request.session.get('otp_verified'):
        return redirect('email_login')  # Redirect if OTP isn't verified

    if request.method == 'POST':
        user_details_form = UserDetailsForm(request.POST)
        if user_details_form.is_valid():

            # Collect the form data
            first_name = user_details_form.cleaned_data['first_name']
            last_name = user_details_form.cleaned_data['last_name']
            phone_number = user_details_form.cleaned_data['phone_number']
            email = request.session['email']

            # Create the new user with is_active set to True
            user = Account.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
            )
            user.is_active = True  # Set is_active to True
            user.save()  # Save the changes to the user instance

            # Log the user in
            login(request, user)
            return redirect('Home')  # Redirect to home page after successful registration
    else:
        user_details_form = UserDetailsForm()

    return render(request, 'myapp/user_details_form.html', {'form': user_details_form})