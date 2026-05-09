from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import CustomUser
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
from django.utils.encoding import force_str,force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .forms import CustomUserRegistrartionForm  
# Create your views here.

def register_view(request):
    if request.method=='POST':
        form=CustomUserRegistrartionForm(request.POST)
        if form.is_valid():
            user=form.save()
        if user.role=='COMPANY':
            messages.success(request, "Registration successfull! Please wait for admin approval")
            return redirect('login')
        else:
            login(request, user)
            # messages.success(request,"Registration successfull ! You can now login")
            return redirect('candidate_dashboard')
    else:
        form=CustomUserRegistrartionForm()
    return render(request,'accounts/register.html', {"form": form})

def login_view(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user= authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            if user.role=='COMPANY':
                if not user.is_approved:
                    logout(request)
                    messages.error(request, 'Your company account is not approved yet.')
                    return redirect('login')
                return redirect('company_dashboard')
            else:
                return redirect('candidate_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')
def logout_view(request):
    logout(request)
    # messages.success(request,'Logout Successful')
    return redirect('login')

def custom_forget_password(request):
    if request.method=='POST':
        email=request.POST.get('email')
        users=CustomUser.objects.filter(email=email)

        if users.exists():
            for user in users:
                uid =urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = f"{request.scheme}://{request.get_host()}/auth/reset-password/{uid}/{token}"
                #Email
                subject="Reset Your Password"
                email_template ='accounts/email/forget_password_email.html'
                parameters={
                    'user':user,
                    'reset_url':reset_url,
                }
                msg_html=render_to_string(email_template,parameters)
                # send email
                send_email(
                    subject,
                    "Please reset your password using link provided below",
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    html_message=msg_html,
                )
            messages.success(request, 'Password reset link send to your email')
            return redirect('login')
        else:
            messages.error(request, 'No user found with this email address')
    return render(request, 'accounts/forget_password.html')



def custom_password_reset_confirm(request, uidb64, token):
    try:
        # 1.Decode the user ID
        uid=force_str(urlsafe_base64_decode(uidb64))
        user=CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user= None
    # step2 Chck if token is valid for specific user
    if user is not None and default_token_generator.check_token(user, token):
        if request.method =='POST':
            new_password = request.POST.get('new_password')
            confirm_password= request.POST.get('confirm_password')

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your passwoed has been succesfully reset. Login now with new password")
                return redirect('login')
            else:
                messages.error(request,"Passwords do not match")
        # If GET request or password dont match show the form
        return render(request,'accounts/password_reset_confirm.html')
    else:
        #Token is invalid or expired
        return render(request, 'accounts/password_reset_invalid.html')