from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Gym, GymPhoto, GymPlan, Booking, Customer, GymOwner

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class GymPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymPhoto
        fields = ['id', 'image', 'caption', 'is_primary']

class GymPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymPlan
        fields = ['id', 'name', 'duration', 'price', 'features', 'is_popular']

class GymOwnerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = GymOwner
        fields = ['id', 'user', 'phone_number', 'photo']

class GymSerializer(serializers.ModelSerializer):
    owner = GymOwnerSerializer(read_only=True)
    photos = GymPhotoSerializer(many=True, read_only=True)
    plans = GymPlanSerializer(many=True, read_only=True)
    distance = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = Gym
        fields = [
            'id', 'name', 'description', 'address', 'city', 
            'latitude', 'longitude', 'google_maps_link', 
            'phone_number', 'email', 'opening_time', 'closing_time', 
            'rating', 'is_active', 'owner', 'photos', 'plans', 'distance'
        ]

class BookingSerializer(serializers.ModelSerializer):
    gym_name = serializers.CharField(source='gym.name', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'gym_name', 'plan_name', 'amount', 
            'payment_status', 'start_date', 'end_date', 'access_code', 'created_at'
        ]
