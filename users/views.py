import logging
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

from django.utils.encoding import force_bytes  # Import this

# Function to generate email verification token
def generate_email_verification_token(user):
    uid = urlsafe_base64_encode(str(user.pk).encode())
    token = default_token_generator.make_token(user)
    logger.debug(f'Generated UID: {uid}, Token: {token}')
    return uid, token

# User Registration View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Ensure the user is inactive until they verify their email
            user.save()

            # Generate the UID and token for email verification
            uid = urlsafe_base64_encode(str(user.pk).encode())
            token = default_token_generator.make_token(user)
            verification_url = f'http://{get_current_site(request).domain}/users/verify-email/{uid}/{token}/'

            # Log the verification URL for debugging
            logger.debug(f'Verification URL: {verification_url}')

            # Send verification email
            subject = "Email Verification"
            message = render_to_string('users/verification_email.html', {
                'user': user,
                'verification_url': verification_url,
            })
            send_mail(subject, message, 'admin@auctionplatform.com', [user.email])

            return redirect('email_verification_sent')  # Redirect to an email confirmation page
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})

# User Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# User Logout View
def logout_view(request):
    logout(request)
    return redirect('home')

def verify_email(request, uidb64, token):
    try:
        # Decode the UID
        uid = urlsafe_base64_decode(uidb64).decode()
        logger.debug(f'Decoded UID: {uid}')
        user = User.objects.get(pk=uid)

        # Check if the token matches
        if default_token_generator.check_token(user, token):
            # Token is valid, activate user or update status
            user.is_active = True
            user.save()
            messages.success(request, 'Your email has been verified!')
            return redirect('login')  # Redirect to the login page (or other page)
        else:
            messages.error(request, 'Invalid verification link.')
            return redirect('home')  # Redirect to home if token is invalid

    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.error(f'Error during email verification: {e}')
        messages.error(request, 'Invalid verification link.')
        return redirect('home')

# Email Verification Sent Page
def email_verification_sent(request):
    return render(request, 'users/email_verification_sent.html')

# Verification Failed Page
def verification_failed(request):
    return render(request, 'users/verification_failed.html')
