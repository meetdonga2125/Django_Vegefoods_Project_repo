from django.shortcuts import render, redirect
from .models import User,Fruitage,Wishlist,Cart
from django.conf import settings
from django.core.mail import send_mail
import requests
import random
import stripe
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from django.http import JsonResponse

# Create your views here.


stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'




def validate_signup(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)


@csrf_exempt
def create_checkout_session(request):
	amount = int(json.load(request)['post_data'])
	final_amount=amount*100
	
	session = stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
			'price_data': {
				'currency': 'inr',
				'product_data': {
					'name': 'Checkout Session Data',
					},
				'unit_amount': final_amount,
				},
			'quantity': 1,
			}],
		mode='payment',
		success_url=YOUR_DOMAIN + '/success.html',
		cancel_url=YOUR_DOMAIN + '/cancel.html',)
	return JsonResponse({'id': session.id})

def success(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		i.payment_status=True
		i.save()
		
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')


def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=True)
	return render(request,'myorder.html',{'carts':carts})


def seller_order(request):
	seller=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(payment_status=True)
	orders=[]
	for i in carts:
		if i.product.seller==seller:
			orders.append(i)
	print(orders)
	return render(request,'seller-order.html',{'orders':orders})

def index(request):
    return render(request, 'index.html')


def seller_index(request):
    return render(request, 'seller-index.html')


def signup(request):
    if request.method=='POST':
        try:
            User.objects.get(email=request.POST['email'])
            msg = 'Email Already Registered'
            return render(request, 'signup.html', {'msg': msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    address=request.POST['address'],
                    password=request.POST['password'],
                    profile_pic=request.FILES['profile_pic'],
                    usertype=request.POST['usertype'],
                )
                msg="User Signup Successfully"
                return render(request, 'signup.html', {'msg': msg})
            else:
                msg="password and confirm password does not matched"
                return render(request, 'signup.html', {'msg': msg})
    else:        
        return render(request, 'signup.html')


def login(request):
    if request.method=='POST':
        try:
            user=User.objects.get(email=request.POST['email'])
            if user.password==request.POST['password']:
                request.session['email']=user.email
                request.session['fname']=user.fname
                if user.usertype=='buyer':
                    wishlists=Wishlist.objects.filter(user=user)
                    request.session['wishlist_count']=len(wishlists)
                    carts=Wishlist.objects.filter(user=user,payment_status=False)
                    request.session['cart_count']=len(carts)
                    return render(request,'index.html')
                else:
                    return render(request,'seller-index.html')
            else:
                msg='Incorrect Password'
                return render(request,'login.html', {'msg': msg})
                
        except:
            msg='User Not Registered'
            return render(request, 'login.html', {'msg': msg})    
    else:
        return render(request, 'login.html')
    

def logout(request):
    try:
        del request.session["email"]
        del request.session['fname']
        return render(request, 'login.html')
    except:
        return render(request, 'login.html')
    

def change_password(request):
    user = User.objects.get(email=request.session['email'])
    if request.method=='POST':
        if user.password==request.POST['old_password']:
            if request.POST['new_password']==request.POST['cnew_password']:
                user.password=request.POST['new_password']
                user.save()
                return redirect('logout')
            else:
                msg='new password and confirm new password does not matched'
                if user.usertype=='buyer':
                    return render(request, 'change-password.html', {'msg': msg})
                else:
                    return render(request,'seller-change-password.html',{'msg': msg})  
        else: 
            msg='Incorrect Password'
            if user.usertype=='buyer':
                return render(request, 'change-password.html', {'msg': msg})
            else:
                return render(request,'seller-change-password.html',{'msg': msg})  

    else:  
         if user.usertype=='buyer':
             return render(request, 'change-password.html')
         else:
             return render(request,'seller-change-password.html')  


def forgot_password(request):
    if request.method=='POST':
        try:
            user=User.objects.get(email=request.POST['email'])
            otp=random.randint(1000,9999)
            subject = 'OTP For Forgot Password'
            message = f'Hi  {user.fname}, Your OTP For Forgot Password Is {otp}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail( subject, message, email_from, recipient_list)
            return render(request,'otp.html',{'otp':otp,'email':user.email})
        except:
            msg='Email Not Registered'
            return render(request,'forgot-password.html', {'msg':msg})
        
    else:
        return render(request, 'forgot-password.html')     


def verify_otp(request):
    otp=request.POST['otp']
    email=request.POST['email']
    uotp=request.POST['uotp']

    if otp==uotp:
        return render(request, 'new-password.html', {'email': email})
    else:
        msg='Incorrect OTP'
        return render(request, 'otp.html', {'otp':otp, 'email':email, 'msg': msg})
    

def new_password(request):
    email=request.POST['email']
    np=request.POST['np']
    cnp=request.POST['cnp']
    
    if np==cnp:
        user=User.objects.get(email=email)
        user.password=np
        user.save()
        return render(request,'login.html') 
    else:
        msg='New Password And Confirm New Password Does Not Matched'
        return render(request, 'new-password.html', {'email':email, 'msg':msg})   


def shop(request):
    products=Fruitage.objects.all()
    return render(request, 'shop.html', {'products':products})



def blog(request):
    return render(request, 'blog.html')


def product_single(request):
    return render(request, 'product-single.html')



def checkout(request):
    return render(request, 'checkout.html')


def contact(request):
    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')



def seller_add_product(request):
    if request.method=="POST":
        seller = User.objects.get(email=request.session['email'])
        Fruitage.objects.create(
            seller=seller,
            fruitage_type=request.POST['fruitage_type'],
            fruitage_category=request.POST['fruitage_category'],
            fruitage_name=request.POST['fruitage_name'],
            fruitage_weight=request.POST['fruitage_weight'],
            fruitage_price=request.POST['fruitage_price'],
            fruitage_pic=request.FILES['fruitage_pic'],
        )
        msg='Product Added Sucessfully'
        return render(request,'seller-add-product.html',{'msg':msg})
    
    return render(request, 'seller-add-product.html')


def seller_view_product(request):
    seller=User.objects.get(email=request.session['email'])
    products=Fruitage.objects.filter(seller=seller)
    return render(request,'seller-view-product.html',{'products':products})


def seller_vegetables_product(request):
    seller=User.objects.get(email=request.session['email'])
    products=Fruitage.objects.filter(seller=seller,fruitage_type='vegetables')
    return render(request, 'seller-view-product.html', {'products': products})  



def vegetables_product(request):
    User.objects.get(email=request.session['email'])
    products=Fruitage.objects.filter(fruitage_type='vegetables')
    return render(request, 'shop.html', {'products': products})  



def seller_fruits_product(request):
    seller=User.objects.get(email=request.session['email'])
    products=Fruitage.objects.filter(seller=seller,fruitage_type='fruits')
    return render(request, 'seller-view-product.html', {'products': products})  


def fruits_product(request):
    User.objects.get(email=request.session['email'])
    products=Fruitage.objects.filter(fruitage_type='fruits')
    return render(request, 'shop.html', {'products': products})  



def seller_all_product(request):
    seller=User.objects.get(email=request.session['email'])
    products=Fruitage.objects.filter(seller=seller)
    return render(request, 'seller-view-product.html', {'products': products})  


def all_product(request):
    User.objects.get(email=request.session['email'])
    products=Fruitage.objects.all()
    return render(request, 'shop.html', {'products': products})  



def seller_product_details(request,pk):
    fruitage=Fruitage.objects.get(pk=pk)
    return render(request, 'seller-product-details.html', {'fruitage':fruitage})


def seller_product_edit(request,pk):
    fruitage=Fruitage.objects.get(pk=pk)
    if request.method=='POST':
        fruitage.fruitage_type=request.POST['fruitage_type']
        fruitage.fruitage_category=request.POST['fruitage_category']
        fruitage.fruitage_name=request.POST['fruitage_name']
        fruitage.fruitage_weight=request.POST['fruitage_weight']
        fruitage.fruitage_price=request.POST['fruitage_price']
        try:
            fruitage.fruitage_pic=request.FILES['fruitage_pic']
        except:
            pass   
        fruitage.save()
        msg='Product Updated Sucessfully'
        return render(request, 'seller-product-edit.html',{'msg':msg, 'fruitage':fruitage})
    else:
        return render(request, 'seller-product-edit.html', {'fruitage':fruitage})
    

def seller_product_delete(request,pk):
    fruitage=Fruitage.objects.get(pk=pk)  
    fruitage.delete()
    msg='Fruitage Deleted Successfully'
    seller=User.objects.get(email=request.session['email'])
    products=Fruitage.objects.filter(seller=seller)
    return render(request,'seller-view-product.html',{'products':products, 'msg':msg})



def product_details(request,pk):
    wishlist_flag=False
    cart_flag=False
    user=User.objects.get(email=request.session['email'])
    fruitage=Fruitage.objects.get(pk=pk)
    try:
        Wishlist.objects.get(user=user,fruitage=fruitage)
        wishlist_flag=True
    except:
        pass   
    try:
        Cart.objects.get(user=user,fruitage=fruitage)
        cart_flag=True
    except:
        pass   
    return render(request, 'product-details.html', {'fruitage':fruitage, 'wishlist_flag':wishlist_flag, 'cart_flag':cart_flag})


def add_to_wishlist(request,pk):
    fruitage=Fruitage.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Wishlist.objects.create(user=user,fruitage=fruitage)
    return redirect('wishlist')


def wishlist(request):
    user=User.objects.get(email=request.session['email'])
    wishlists = Wishlist.objects.filter(user=user)
    request.session['wishlist_count']=len(wishlists)
    return render(request, 'wishlist.html',{'wishlists':wishlists})


def remove_from_wishlist(request,pk):
    fruitage=Fruitage.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    wishlist=Wishlist.objects.get(user=user,fruitage=fruitage)
    wishlist.delete()
    return redirect('wishlist')



def add_to_cart(request,pk):
    fruitage=Fruitage.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Cart.objects.create(
        user=user,
        fruitage=fruitage,
        fruitage_price=fruitage.fruitage_price,
        fruitage_qty=1,
        total_price=fruitage.fruitage_price,
        payment_status=False
        )
    return redirect('cart')


def cart(request):
    net_price=0
    user=User.objects.get(email=request.session['email'])
    carts = Cart.objects.filter(user=user,payment_status=False)
    for i in carts:
        net_price=net_price + i.total_price
    request.session['cart_count']=len(carts)
    return render(request, 'cart.html',{'carts':carts, 'net_price': net_price})


def remove_from_cart(request,pk):
    fruitage=Fruitage.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    cart=Cart.objects.get(user=user,fruitage=fruitage)
    cart.delete()
    return redirect('cart')


def change_qty(request):
    cid=int(request.POST['cid'])
    fruitage_qty=int(request.POST['fruitage_qty'])
    cart=Cart.objects.get(pk=cid)
    fruitage_price=cart.fruitage.fruitage_price
    cart.total_price=fruitage_price*fruitage_qty
    cart.fruitage_qty=fruitage_qty
    cart.save()
    return redirect('cart')

    











