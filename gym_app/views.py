from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from .forms import SignUpForm, LoginForm, PaymentForm
from .models import Member, Payment
import qrcode
from io import BytesIO
import base64

def member_profile(request):
    member = get_object_or_404(Member, user=request.user)
    payments = Payment.objects.filter(member=member).order_by('-payment_date')
    
    # Generate QR Code
    qr_data = f"MuscleMeter Member: {member.user.username} (ID: {member.id})"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer)
    qr_image = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'member': member,
        'payments': payments,
        'qr_image': qr_image
    }
    return render(request, 'gym_app/member_profile.html', context)

def auth_register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to MuscleMeter! Your account has been created.')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'gym_app/register.html', {'form': form})

def auth_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'gym_app/login.html', {'form': form})

def auth_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def home(request):
    return render(request, 'gym_app/home.html')

# --- Admin Views ---

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    total_members = Member.objects.count()
    active_members = Member.objects.filter(subscription_status=True).count()
    total_revenue = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    recent_payments = Payment.objects.order_by('-payment_date')[:5]
    
    active_percentage = (active_members / total_members * 100) if total_members > 0 else 0

    context = {
        'total_members': total_members,
        'active_members': active_members,
        'total_revenue': total_revenue,
        'recent_payments': recent_payments,
        'active_percentage': active_percentage,
    }
    return render(request, 'gym_app/admin_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_member_list(request):
    members = Member.objects.select_related('user').all()
    return render(request, 'gym_app/admin_member_list.html', {'members': members})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def payment_add(request):
    # This view would typically be a modal or separate page, skipping detailed impl for now to focus on dashboard
    # But for completeness of the link in dashboard:
    messages.info(request, "Payment Module Coming Soon")
    return redirect('admin_dashboard')
