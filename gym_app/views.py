from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid
import qrcode
from io import BytesIO
import base64
import math

from .forms import (
    CustomerSignUpForm, GymOwnerSignUpForm, LoginForm,
    GymRegistrationForm, GymPhotoForm, GymPlanForm, BookingForm
)
from .models import Gym, GymPhoto, GymPlan, Customer, GymOwner, Booking


def landing_page(request):
    """Landing page with role selection."""
    return render(request, 'gym_app/landing.html')


def customer_register(request):
    """Customer registration page."""
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to MuscleMeter! Start exploring gyms near you.')
            return redirect('explore')
    else:
        form = CustomerSignUpForm()
    return render(request, 'gym_app/customer_register.html', {'form': form})


def owner_register(request):
    """Gym owner registration page."""
    if request.method == 'POST':
        form = GymOwnerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Now register your gym to get started.')
            return redirect('gym_register')
    else:
        form = GymOwnerSignUpForm()
    return render(request, 'gym_app/owner_register.html', {'form': form})


def auth_login(request):
    """Login page for both customers and owners."""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Redirect based on user type
            if hasattr(user, 'gym_owner_profile'):
                return redirect('owner_dashboard')
            return redirect('explore')
    else:
        form = LoginForm()
    return render(request, 'gym_app/login.html', {'form': form})


def auth_logout(request):
    """Logout user."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('landing')


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(float(lat1))
    lat2_rad = math.radians(float(lat2))
    delta_lat = math.radians(float(lat2) - float(lat1))
    delta_lon = math.radians(float(lon2) - float(lon1))
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def explore(request):
    """Gym discovery page with location-based results."""
    gyms = Gym.objects.filter(is_active=True).prefetch_related('photos', 'plans')
    
    # Get user location from query params (set by JavaScript)
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
    
    gyms_with_distance = []
    for gym in gyms:
        gym_data = {
            'gym': gym,
            'primary_photo': gym.photos.filter(is_primary=True).first() or gym.photos.first(),
            'min_price': gym.plans.filter(is_active=True).order_by('price').first(),
            'distance': None
        }
        
        if user_lat and user_lon:
            distance = calculate_distance(user_lat, user_lon, gym.latitude, gym.longitude)
            gym_data['distance'] = round(distance, 1)
        
        gyms_with_distance.append(gym_data)
    
    # Sort by distance if available
    if user_lat and user_lon:
        gyms_with_distance.sort(key=lambda x: x['distance'] or 999)
    
    context = {
        'gyms': gyms_with_distance,
        'user_lat': user_lat,
        'user_lon': user_lon,
    }
    return render(request, 'gym_app/explore.html', context)


def gym_detail(request, gym_id):
    """Gym detail page with photos, plans, and contact info."""
    gym = get_object_or_404(Gym, id=gym_id, is_active=True)
    photos = gym.photos.all()
    plans = gym.plans.filter(is_active=True)
    
    # Get user location for distance
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
    distance = None
    
    if user_lat and user_lon:
        distance = round(calculate_distance(user_lat, user_lon, gym.latitude, gym.longitude), 1)
    
    context = {
        'gym': gym,
        'photos': photos,
        'plans': plans,
        'distance': distance,
        'primary_photo': photos.filter(is_primary=True).first() or photos.first(),
    }
    return render(request, 'gym_app/gym_detail.html', context)


@login_required
def checkout(request, gym_id, plan_id):
    """Checkout page for booking a gym plan."""
    gym = get_object_or_404(Gym, id=gym_id, is_active=True)
    plan = get_object_or_404(GymPlan, id=plan_id, gym=gym, is_active=True)
    
    # Ensure user is a customer
    if not hasattr(request.user, 'customer_profile'):
        messages.error(request, 'Please register as a customer to book.')
        return redirect('customer_register')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Calculate booking dates based on plan duration
            start_date = timezone.now().date()
            duration_map = {
                'day': 1,
                'week': 7,
                'month': 30,
                'quarter': 90,
                'half_year': 180,
                'year': 365,
            }
            days = duration_map.get(plan.duration, 30)
            end_date = start_date + timedelta(days=days)
            
            # Create booking with simulated payment
            booking = Booking.objects.create(
                customer=request.user.customer_profile,
                gym=gym,
                plan=plan,
                amount=plan.price,
                payment_status='completed',  # Simulated success
                payment_id=f"SIM_{uuid.uuid4().hex[:12].upper()}",
                start_date=start_date,
                end_date=end_date,
            )
            
            messages.success(request, 'Booking confirmed! Your gym pass is ready.')
            return redirect('booking_success', booking_id=booking.booking_id)
    else:
        form = BookingForm(initial={'plan_id': plan.id})
    
    context = {
        'gym': gym,
        'plan': plan,
        'form': form,
    }
    return render(request, 'gym_app/checkout.html', context)


def booking_success(request, booking_id):
    """Booking confirmation page with QR code."""
    booking = get_object_or_404(Booking, booking_id=booking_id)
    
    # Verify booking belongs to current user (if logged in)
    if request.user.is_authenticated:
        if hasattr(request.user, 'customer_profile'):
            if booking.customer != request.user.customer_profile:
                messages.error(request, 'Access denied.')
                return redirect('explore')
    
    # Generate QR code
    qr_data = f"MuscleMeter Pass\nCode: {booking.access_code}\nGym: {booking.gym.name}\nValid: {booking.start_date} to {booking.end_date}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#CCFF00", back_color="#121212")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_image = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'booking': booking,
        'qr_image': qr_image,
    }
    return render(request, 'gym_app/booking_success.html', context)


@login_required
def owner_dashboard(request):
    """Dashboard for gym owners to manage their gyms."""
    if not hasattr(request.user, 'gym_owner_profile'):
        messages.error(request, 'Access denied. This area is for gym owners only.')
        return redirect('landing')
    
    owner = request.user.gym_owner_profile
    gyms = owner.gyms.all().prefetch_related('photos', 'plans', 'bookings')
    
    # Calculate stats
    total_bookings = sum(gym.bookings.count() for gym in gyms)
    total_revenue = sum(
        sum(b.amount for b in gym.bookings.filter(payment_status='completed'))
        for gym in gyms
    )
    
    context = {
        'owner': owner,
        'gyms': gyms,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
    }
    return render(request, 'gym_app/owner_dashboard.html', context)


@login_required
def gym_register(request):
    """Register a new gym (for gym owners)."""
    if not hasattr(request.user, 'gym_owner_profile'):
        messages.error(request, 'Please register as a gym owner first.')
        return redirect('owner_register')
    
    if request.method == 'POST':
        gym_form = GymRegistrationForm(request.POST)
        photo_form = GymPhotoForm(request.POST, request.FILES)
        
        if gym_form.is_valid() and photo_form.is_valid():
            gym = gym_form.save(commit=False)
            gym.owner = request.user.gym_owner_profile
            gym.save()
            
            # Save photos
            photos = photo_form.get_photos()
            for i, photo in enumerate(photos):
                GymPhoto.objects.create(
                    gym=gym,
                    image=photo,
                    is_primary=(i == 0)  # First photo is primary
                )
            
            messages.success(request, f'{gym.name} has been registered! Now add your plans.')
            return redirect('gym_add_plans', gym_id=gym.id)
    else:
        gym_form = GymRegistrationForm()
        photo_form = GymPhotoForm()
    
    context = {
        'gym_form': gym_form,
        'photo_form': photo_form,
    }
    return render(request, 'gym_app/gym_register.html', context)


@login_required
def gym_add_plans(request, gym_id):
    """Add plans to a gym."""
    gym = get_object_or_404(Gym, id=gym_id)
    
    # Verify ownership
    if gym.owner.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('owner_dashboard')
    
    if request.method == 'POST':
        form = GymPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.gym = gym
            plan.save()
            messages.success(request, f'Plan "{plan.name}" added!')
            
            if 'add_another' in request.POST:
                return redirect('gym_add_plans', gym_id=gym.id)
            return redirect('owner_dashboard')
    else:
        form = GymPlanForm()
    
    existing_plans = gym.plans.all()
    
    context = {
        'gym': gym,
        'form': form,
        'existing_plans': existing_plans,
    }
    return render(request, 'gym_app/gym_add_plans.html', context)


def update_location(request):
    """API endpoint to update customer's last known location."""
    if request.method == 'POST' and request.user.is_authenticated:
        if hasattr(request.user, 'customer_profile'):
            import json
            data = json.loads(request.body)
            customer = request.user.customer_profile
            customer.last_latitude = data.get('latitude')
            customer.last_longitude = data.get('longitude')
            customer.last_city = data.get('city', '')
            customer.save()
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)
