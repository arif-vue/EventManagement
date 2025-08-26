from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.urls import reverse
from .forms import SignUpForm
from events.models import UserProfile

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Assign role based on user selection
            selected_role = form.cleaned_data.get('role', 'Participant')
            role_group, created = Group.objects.get_or_create(name=selected_role)
            user.groups.add(role_group)
            
            # Create user profile with activation token
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Send activation email with explicit domain
            current_site = get_current_site(request)
            # Use request host for development, or hardcode for consistency
            domain = request.get_host() if request.get_host() else '127.0.0.1:8000'
            protocol = 'https' if request.is_secure() else 'http'
            
            mail_subject = 'Activate your Event Management account'
            activation_url = f"{protocol}://{domain}/accounts/activate/{profile.activation_token}/"
            
            print(f"DEBUG: Generated activation URL: {activation_url}")  # Debug line
            
            message = render_to_string('accounts/activation_email_simple.html', {
                'user': user,
                'domain': domain,
                'activation_url': activation_url,
                'protocol': protocol,
            })
            
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.content_subtype = 'html'
            email.send()
            
            messages.success(request, 'Registration successful! Please check your email to activate your account.')
            return redirect('login')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def activate(request, activation_token):
    try:
        profile = UserProfile.objects.get(activation_token=activation_token)
        user = profile.user
        
        if not user.is_active:
            user.is_active = True
            user.save()
            
            profile.is_activated = True
            profile.save()
            
            messages.success(request, 'Your account has been activated successfully! You can now log in.')
            return redirect('login')
        else:
            messages.info(request, 'Your account is already activated. You can log in.')
            return redirect('login')
            
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid activation link.')
        return redirect('signup')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                # Check if user is activated
                try:
                    profile = user.userprofile
                    if not profile.is_activated:
                        messages.error(request, 'Please activate your account before logging in.')
                        return render(request, 'accounts/login.html')
                except UserProfile.DoesNotExist:
                    # Create profile for existing users without profile
                    UserProfile.objects.create(user=user, is_activated=True)
                
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Your account is not active. Please check your email for activation instructions.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def profile_view(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user, is_activated=True)
    
    user_groups = request.user.groups.all()
    context = {
        'profile': profile,
        'user_groups': user_groups,
    }
    return render(request, 'accounts/profile.html', context)

def test_activation_url(request):
    """Debug view to test activation URL generation"""
    # Create a test user for debugging (you can remove this later)
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'is_active': False}
    )
    
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=test_user)
    
    # Use request host for development
    domain = request.get_host() if request.get_host() else '127.0.0.1:8000'
    protocol = 'https' if request.is_secure() else 'http'
    activation_url = f"{protocol}://{domain}/accounts/activate/{profile.activation_token}/"
    
    return HttpResponse(f"""
    <h1>Debug Activation URL (UUID-based)</h1>
    <p><strong>Test User:</strong> {test_user.username}</p>
    <p><strong>User Active:</strong> {test_user.is_active}</p>
    <p><strong>Profile Activated:</strong> {profile.is_activated}</p>
    <p><strong>Activation Token:</strong> {profile.activation_token}</p>
    <p><strong>Domain:</strong> {domain}</p>
    <p><strong>Protocol:</strong> {protocol}</p>
    <p><strong>Full URL:</strong> <a href="{activation_url}" target="_blank">{activation_url}</a></p>
    <p>Click the link above to test activation</p>
    <hr>
    <p><a href="/accounts/signup/">Test Signup</a> | <a href="/accounts/login/">Test Login</a></p>
    <hr>
    <h3>Site Configuration:</h3>
    <p>Current Host: {request.get_host()}</p>
    <p>Is Secure: {request.is_secure()}</p>
    """)

from django.http import HttpResponse
