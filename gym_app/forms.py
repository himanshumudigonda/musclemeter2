from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import GymOwner, Gym, GymPhoto, GymPlan, Customer, Booking


class CustomerSignUpForm(UserCreationForm):
    """Registration form for customers."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address'
    }))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First name'
    }))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last name'
    }))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone number'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number', '')
            )
        return user


class GymOwnerSignUpForm(UserCreationForm):
    """Registration form for gym owners."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address'
    }))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First name'
    }))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last name'
    }))
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone number'
    }))
    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'image/*'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            GymOwner.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                photo=self.cleaned_data.get('photo')
            )
        return user


class LoginForm(AuthenticationForm):
    """Custom styled login form."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })


class GymRegistrationForm(forms.ModelForm):
    """Form for registering a new gym."""
    class Meta:
        model = Gym
        fields = [
            'name', 'description', 'address', 'city',
            'latitude', 'longitude', 'google_maps_link',
            'phone_number', 'email', 'opening_time', 'closing_time'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Gym name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your gym...',
                'rows': 4
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Full address',
                'rows': 2
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Latitude',
                'step': '0.000001',
                'id': 'id_latitude'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Longitude',
                'step': '0.000001',
                'id': 'id_longitude'
            }),
            'google_maps_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Google Maps share link (optional)'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact email (optional)'
            }),
            'opening_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'closing_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
        }


class GymPhotoForm(forms.Form):
    """Form for uploading gym photos (up to 5)."""
    photo1 = forms.ImageField(required=True, widget=forms.FileInput(attrs={
        'class': 'form-control photo-input',
        'accept': 'image/*'
    }))
    photo2 = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control photo-input',
        'accept': 'image/*'
    }))
    photo3 = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control photo-input',
        'accept': 'image/*'
    }))
    photo4 = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control photo-input',
        'accept': 'image/*'
    }))
    photo5 = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control photo-input',
        'accept': 'image/*'
    }))

    def get_photos(self):
        """Return list of non-empty photos."""
        photos = []
        for i in range(1, 6):
            photo = self.cleaned_data.get(f'photo{i}')
            if photo:
                photos.append(photo)
        return photos


class GymPlanForm(forms.ModelForm):
    """Form for adding/editing gym plans."""
    class Meta:
        model = GymPlan
        fields = ['name', 'duration', 'price', 'features', 'is_popular']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Plan name (e.g., "Basic", "Premium")'
            }),
            'duration': forms.Select(attrs={
                'class': 'form-select'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Price in ₹',
                'min': '0',
                'step': '0.01'
            }),
            'features': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Features (comma-separated, e.g., "Gym access, Locker, Trainer support")',
                'rows': 3
            }),
            'is_popular': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class BookingForm(forms.Form):
    """Form for booking a gym plan."""
    plan_id = forms.IntegerField(widget=forms.HiddenInput())
    
    # Simulated payment fields
    card_number = forms.CharField(max_length=19, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '1234 5678 9012 3456',
        'maxlength': '19'
    }))
    card_expiry = forms.CharField(max_length=5, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'MM/YY',
        'maxlength': '5'
    }))
    card_cvv = forms.CharField(max_length=3, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'CVV',
        'maxlength': '3'
    }))
    card_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Name on card'
    }))

    def clean_card_number(self):
        """Basic validation for card number."""
        number = self.cleaned_data['card_number'].replace(' ', '')
        if len(number) < 13 or len(number) > 19:
            raise forms.ValidationError("Invalid card number length")
        if not number.isdigit():
            raise forms.ValidationError("Card number must contain only digits")
        return number

    def clean_card_expiry(self):
        """Basic validation for expiry date."""
        expiry = self.cleaned_data['card_expiry']
        if '/' not in expiry:
            raise forms.ValidationError("Use MM/YY format")
        parts = expiry.split('/')
        if len(parts) != 2:
            raise forms.ValidationError("Use MM/YY format")
        return expiry

    def clean_card_cvv(self):
        """Basic validation for CVV."""
        cvv = self.cleaned_data['card_cvv']
        if not cvv.isdigit() or len(cvv) != 3:
            raise forms.ValidationError("CVV must be 3 digits")
        return cvv
