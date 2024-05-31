from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from shop.models import Product
from cart.models import Cart
from cart.models import Account,Order



def cartview(request):
    total=0
    u=request.user
    try:
        cart=Cart.objects.filter(user=u)

        for i in cart:
            total+=i.quantity*i.product.price
    except:
        pass
    return render(request,'cart.html',{'c':cart,'total':total})


@login_required
def add_to_cart(request,p):
    product=Product.objects.get(name=p)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=product)
        if(cart.quantity<cart.product.stock):
          cart.quantity+=1
          cart.save()
    except:
        cart=Cart.objects.create(product=product,user=u,quantity=1)
        cart.save()

    return redirect('cart:cartview')


def cart_remove(request,p):
    product=Product.objects.get(name=p)
    user=request.user
    try:
        cart=Cart.objects.get(user=user,product=product)
        if(cart.quantity>1):
            cart.quantity-=1
            cart.save()
        else:
            cart.delete()
    except:
        pass
    return redirect('cart:cartview')

def full_remove(request,p):
    product=Product.objects.get(name=p)
    user=request.user
    try:
        cart=Cart.objects.get(user=user,product=product)

        cart.delete()
    except:
        pass
    return redirect('cart:cartview')


def orderform(request):
    if(request.method=="POST"):
        a=request.POST['a']
        p=request.POST['p']
        n=request.POST['n']
        u=request.user
        cart=Cart.objects.filter(user=u)

        #total amount
        total=0
        for i in cart:
            total+=i.quantity*i.product.price


        #to check whether user has sifficient money in account
        ac=Account.objects.get(acctnum=n)
        if(ac.amount>=total):
            ac.amount=ac.amount-total
            ac.save()

            for i in cart: #creates record in order table for each object in Cart table for the current user
                o=Order.objects.create(user=u,product=i.product,address=a,phone=p,no_of_items=i.quantity,order_status="paid")
                o.save()
                i.product.stock=i.product.stock-i.quantity
                i.product.save()
            cart.delete()
            msg="Order placed successfully"
            return render(request,'orderdetail.html',{'m':msg})
        else:
            msg="Insufficient amount in user account.You cannot place order"
            return render(request,'orderdetail.html',{'m':msg})

    return render(request,'orderform.html')

def orderview(request):
    u=request.user
    o=Order.objects.filter(user=u)
    return render(request,'orderview.html',{'u':u.username,'o':o})