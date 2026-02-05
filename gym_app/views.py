from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
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
    
    is_owner = False
    if request.user.is_authenticated and hasattr(request.user, 'gym_owner_profile'):
        is_owner = (request.user.gym_owner_profile == gym.owner)

    context = {
        'gym': gym,
        'photos': photos,
        'plans': plans,
        'distance': distance,
        'primary_photo': photos.filter(is_primary=True).first() or photos.first(),
        'is_owner': is_owner,
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


@login_required
def gym_edit_plan(request, gym_id, plan_id):
    """Edit an existing gym plan."""
    gym = get_object_or_404(Gym, id=gym_id)
    plan = get_object_or_404(GymPlan, id=plan_id, gym=gym)
    
    # Verify ownership
    if gym.owner.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('owner_dashboard')
    
    if request.method == 'POST':
        form = GymPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f'Plan "{plan.name}" updated successfully!')
            return redirect('owner_dashboard')
    else:
        form = GymPlanForm(instance=plan)
    
    context = {
        'gym': gym,
        'plan': plan,
        'form': form,
    }
    return render(request, 'gym_app/gym_edit_plan.html', context)

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
# === REST API Views ===
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import GymSerializer, GymPlanSerializer, BookingSerializer, GymOwnerSerializer

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

# Initialize Firebase (Try/Except to avoid errors if already init or missing creds during build)
try:
    if not firebase_admin._apps:
        # In production, we typically use environment variable for creds or default
        firebase_admin.initialize_app()
except Exception as e:
    print(f"Firebase Init Warning: {e}")

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_google_auth(request):
    token = request.data.get('token')
    requested_role = request.data.get('role')  # 'owner' or 'customer'
    
    if not token:
        return Response({'error': 'No token provided'}, status=400)
    
    try:
        # Verify Token
        try:
            decoded_token = firebase_auth.verify_id_token(token)
        except Exception:
            # Fallback for dev/testing if needed, or strict fail
            raise Exception("Invalid Token")

        email = decoded_token['email']
        
        # Get or Create User
        user, created = User.objects.get_or_create(username=email, defaults={
            'email': email,
            'first_name': decoded_token.get('name', '').split(' ')[0],
            'last_name': ' '.join(decoded_token.get('name', '').split(' ')[1:])
        })
        
        # Log them in
        login(request, user)
        
        # Check Existing Roles
        is_owner = hasattr(user, 'gym_owner_profile')
        is_customer = hasattr(user, 'customer_profile')
        
        assigned_role = 'customer' # Default
        
        if is_owner:
            assigned_role = 'owner'
        elif is_customer:
            assigned_role = 'customer'
        else:
            # New User - Assign Role
            if requested_role == 'owner':
                GymOwner.objects.create(user=user)
                assigned_role = 'owner'
            else:
                Customer.objects.create(user=user)
                assigned_role = 'customer'

        return Response({
            'success': True,
            'username': user.username,
            'role': assigned_role
        })
        
    except Exception as e:
        print(f"Auth Error: {e}")
        return Response({'error': 'Authentication failed'}, status=400)

class GymListAPI(generics.ListAPIView):
    serializer_class = GymSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Gym.objects.filter(is_active=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        
        if lat and lon:
            # Calculate distance using Python (basic implementation, ideally use PostGIS)
            gyms = list(queryset)
            for gym in gyms:
                gym.distance = calculate_distance(lat, lon, gym.latitude, gym.longitude)
            gyms.sort(key=lambda x: x.distance)
            return gyms
        return queryset

class GymDetailAPI(generics.RetrieveAPIView):
    serializer_class = GymSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Gym.objects.filter(is_active=True)
    lookup_field = 'id'

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_create_booking(request, gym_id, plan_id):
    gym = get_object_or_404(Gym, id=gym_id)
    plan = get_object_or_404(GymPlan, id=plan_id)
    
    # Calculate dates
    start_date = timezone.now().date()
    duration_map = {'day': 1, 'week': 7, 'month': 30, 'quarter': 90, 'half_year': 180, 'year': 365}
    days = duration_map.get(plan.duration, 30)
    end_date = start_date + timedelta(days=days)
    
    booking = Booking.objects.create(
        customer=request.user.customer_profile,
        gym=gym,
        plan=plan,
        amount=plan.price,
        payment_status='completed',
        payment_id=f"SIM_{uuid.uuid4().hex[:12].upper()}",
        start_date=start_date,
        end_date=end_date
    )
    
    # Generate QR Code
    qr_data = f"Code: {booking.access_code}\nGym: {booking.gym.name}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return Response({
        'success': True,
        'booking_id': booking.booking_id,
        'access_code': booking.access_code,
        'qr_image': qr_base64
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_owner_dashboard(request):
    if not hasattr(request.user, 'gym_owner_profile'):
        return Response({'error': 'Not authorized'}, status=403)
        
    owner = request.user.gym_owner_profile
    gyms = owner.gyms.all()
    serializer = GymSerializer(gyms, many=True)
    
    total_bookings = sum(gym.bookings.count() for gym in gyms)
    total_revenue = sum(
        sum(b.amount for b in gym.bookings.filter(payment_status='completed'))
        for gym in gyms
    )
    
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_register_customer(request):
    try:
        data = request.data
        if Customer.objects.filter(user__username=data.get('username')).exists():
            return Response({'error': 'Username already exists'}, status=400)
            
        user = User.objects.create_user(
            username=data['username'],
            email=data.get('email', ''),
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        Customer.objects.create(user=user, phone_number=data.get('phone_number', ''))
        
        login(request, user)
        return Response({'success': True, 'username': user.username, 'role': 'customer'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_register_owner(request):
    try:
        data = request.data
        if GymOwner.objects.filter(user__username=data.get('username')).exists():
            return Response({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(
            username=data['username'],
            email=data.get('email', ''),
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        GymOwner.objects.create(user=user, phone_number=data.get('phone_number', ''))
        
        login(request, user)
        return Response({'success': True, 'username': user.username, 'role': 'owner'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_create_gym(request):
    if not hasattr(request.user, 'gym_owner_profile'):
        return Response({'error': 'Not authorized'}, status=403)
    
    try:
        data = request.data
        gym = Gym.objects.create(
            owner=request.user.gym_owner_profile,
            name=data['name'],
            description=data.get('description', ''),
            address=data['address'],
            city=data['city'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            phone_number=data.get('phone_number', ''),
            email=data.get('email', ''),
            opening_time=data.get('opening_time','06:00'),
            closing_time=data.get('closing_time','22:00'),
            is_active=True
        )
        return Response({'success': True, 'gym_id': gym.id})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_create_plan(request, gym_id):
    gym = get_object_or_404(Gym, id=gym_id)
    if gym.owner.user != request.user:
        return Response({'error': 'Not authorized'}, status=403)
        
    try:
        serializer = GymPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(gym=gym)
            return Response({'success': True})
        return Response(serializer.errors, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
