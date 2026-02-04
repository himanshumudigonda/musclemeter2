from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class GymOwner(models.Model):
    """Profile for gym owners who can register and manage gyms."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gym_owner_profile')
    phone_number = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='owner_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Owner: {self.user.get_full_name() or self.user.username}"


class Gym(models.Model):
    """Gym listing with location, details, and owner reference."""
    owner = models.ForeignKey(GymOwner, on_delete=models.CASCADE, related_name='gyms')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    
    # Location coordinates for distance calculation
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    google_maps_link = models.URLField(max_length=500, blank=True)
    
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    
    # Operating hours
    opening_time = models.TimeField(default='06:00')
    closing_time = models.TimeField(default='22:00')
    
    # Ratings and status
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.0,
                                  validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.city})"


class GymPhoto(models.Model):
    """Photos for a gym (up to 5 per gym)."""
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='gym_photos/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-uploaded_at']

    def __str__(self):
        return f"Photo for {self.gym.name}"


class GymPlan(models.Model):
    """Subscription plans offered by a gym."""
    DURATION_CHOICES = [
        ('day', '1 Day Pass'),
        ('week', '1 Week'),
        ('month', '1 Month'),
        ('quarter', '3 Months'),
        ('half_year', '6 Months'),
        ('year', '1 Year'),
    ]

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='plans')
    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.TextField(help_text="Comma-separated list of features")
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.gym.name} - {self.name} (₹{self.price})"

    def get_features_list(self):
        return [f.strip() for f in self.features.split(',') if f.strip()]


class Customer(models.Model):
    """Customer profile for users who book gyms."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Last known location
    last_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_city = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer: {self.user.get_full_name() or self.user.username}"


class Booking(models.Model):
    """Booking record linking customer to a gym plan."""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='bookings')
    plan = models.ForeignKey(GymPlan, on_delete=models.CASCADE, related_name='bookings')
    
    # Payment details (simulated)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=100, blank=True)  # Simulated payment reference
    
    # Booking period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # QR code for gym access
    access_code = models.CharField(max_length=50, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.booking_id} - {self.customer.user.username} at {self.gym.name}"

    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = f"MM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
