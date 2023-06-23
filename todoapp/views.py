from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.forms import UserCreationForm
from todoapp.forms import RegisterForm
from django.contrib.auth.models import User
import random
import datetime
from todoapp.models import Task
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail

# Create your views here.

def dashboard(request):
    #print("Authenticated user id:",request.user.id)
    content={}
    if request.method=="POST":
        #fetch data from form
        name=request.POST['tname']
        det=request.POST['tdetail']
        c=request.POST['cat']
        s=request.POST['status']
        dt=request.POST['duedate']
        #validation
        u=User.objects.filter(id=request.user.id) #fetch auth user object
        t=Task.objects.create(name=name,detail=det,cat=c,status=s,enddate=dt,created_on=datetime.datetime.now(),uid=u[0])
        t.save()
        return redirect('/dashboard')
            
    else:
        # here we see that we see only logged in user task
        q1=Q(uid=request.user.id)
        q2=Q(is_deleted=False)
        t=Task.objects.filter(q1 & q2)
        content['data']=t
        
        return render(request,'todoapp\dashboard.html',content)
    


def user_register(request):
    content={}
    if request.method=='POST':
        un=request.POST['uname']
        p=request.POST['upass']
        cp=request.POST['ucpass']
        if un=='' or p=='' or cp=='':
            content['errmsg']="Fields cannot be Empty"
        elif p!=cp:
            content['errmsg']="Password and confirmed password didn't matched"
        elif len(p)<8:
            content['errmsg']="Password must be atleast 8 chatacters in length"
        else:
            
            try:
                u=User.objects.create(username=un,email=un)
                u.set_password(p)
                u.save()
                content['success']="User register Successfully!! Please Login"
            except Exception:
                content['errmsg']="User with same username already exist"
           
        return render(request,'accounts/register.html',content)
    
    else:
       
        return render(request,'accounts/register.html',)
    

def user_login(request):
    content={}
    if request.method=="POST":
        un=request.POST['uname']
        up=request.POST['upass']
        u=authenticate(username=un,password=up)
        #print(u)
        if u is not None:
            login(request,u)
            return redirect('/dashboard')
        else:
            content['errmsg']="Invalid Username or Password"
            return render(request,'accounts/login.html',content)
        
       # q1=Q(username=un)
        #q2=Q(password=up)
        
       # u=User.objects.filter(q1 & q2)
       # print(len(u))
       
        return HttpResponse("User fetched ")
        
    else:
        return render(request,'accounts/login.html')


def user_logout(request):
    logout(request)#destroy session delete all data from session
    return redirect('/login')

def delete(request,rid):
   # print("Id",rid)
   #we are doing soft delete
   t=Task.objects.filter(id=rid)
   t.update(is_deleted=True)
   return redirect('/dashboard')

def edit(request,rid):
    if request.method=="POST":
        #fetch data from form
        uname=request.POST['tname']
        udet=request.POST['tdetail']
        uc=request.POST['cat']
        us=request.POST['status']
        udt=request.POST['duedate']
       #udt.strftime("%Y-%m-%j")
        t=Task.objects.filter(id=rid)
        t.update(name=uname,detail=udet,cat=uc,status=us,enddate=udt)
        return redirect('/dashboard')
    else:
       # print("Id:",rid)
       t=Task.objects.filter(id=rid)
       content={}
       content['data']=t
      # dt=t[0][1]
       #print(dt.strftime("%d/%m/%Y"))
       return render(request,'todoapp/edit.html',content)
   
def catfilter(request,cv):
    q1=Q(uid=request.user.id)
    q2=Q(is_deleted=False)
    q3=Q(cat=cv)
    t=Task.objects.filter(q1 & q2 & q3)
    content={}
    content['data']=t
    return render(request,'todoapp/dashboard.html',content)

def statusfilter(request,sv):
    q1=Q(uid=request.user.id)
    q2=Q(is_deleted=False)
    q3=Q(status=sv)
    t=Task.objects.filter(q1 & q2 & q3)
    content={}
    content['data']=t
    return render(request,'todoapp/dashboard.html',content)


def datefilter(request):
    frm=request.GET['from']
    to=request.GET['to']
    #print(frm)
    #print(to)
    q1=Q(uid=request.user.id)
    q2=Q(is_deleted=False)
    q3=Q(enddate__gte=frm)
    q4=Q(enddate__lte=to)
    t=Task.objects.order_by('-enddate').filter(q3 & q4).filter(q1 & q2)
    content={}
    content['data']=t

    return render(request,'todoapp/dashboard.html',content)

def datesort(request,dv):
    q1=Q(is_deleted=False)
    q2=Q(uid=request.user.id)
    if dv=='0':
        col="-enddate"
    else:
        col="enddate"
    
    t=Task.objects.order_by(col).filter(q1 & q2)
    content={}
    content['data']=t
    return render(request,'todoapp/dashboard.html',content)


def sendpensingemail(t):
    
    for x in t:
        if x.status==0:
            d=x.enddate.day
            #print(type(d))
            curdt=datetime.datetime.now().day
            #print(curdt)
            diff=d-curdt
            #print(diff)
            if diff==1:
                rec=x.uid.email
                subject="REMINDER"
                msg=x.name+"Task is Due for 1 day"
                sender='kutebhagyashree92@gmail.com'
                send_mail(
                    subject,
                    msg,
                    sender,
                    [rec],
                    fail_silently=False,
                    
                )
                
        