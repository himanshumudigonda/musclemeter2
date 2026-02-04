"""
Management command to create sample gym data for testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gym_app.models import GymOwner, Gym, GymPlan


class Command(BaseCommand):
    help = 'Create sample gym data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create owner user
        owner_user, created = User.objects.get_or_create(
            username='gymowner1',
            defaults={
                'email': 'owner@fitletics.com',
                'first_name': 'Rajesh',
                'last_name': 'Kumar',
            }
        )
        if created:
            owner_user.set_password('demo1234')
            owner_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: gymowner1'))

        # Create gym owner profile
        gym_owner, created = GymOwner.objects.get_or_create(
            user=owner_user,
            defaults={
                'phone_number': '+91 98765 43210'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created gym owner profile'))

        # Create sample gym (FitLetics Hyderabad)
        gym, created = Gym.objects.get_or_create(
            owner=gym_owner,
            name='FitLetics Premium Gym',
            defaults={
                'description': '''Welcome to FitLetics Premium Gym - Hyderabad's most modern fitness destination! 

Our 10,000 sq ft facility features state-of-the-art equipment from Life Fitness and Hammer Strength. We offer dedicated zones for cardio, strength training, functional fitness, and group classes.

✓ Air-conditioned throughout
✓ Premium locker rooms with showers
✓ Certified personal trainers
✓ Protein bar and supplement shop
✓ Free parking

Join the FitLetics family and transform your life!''',
                'address': 'Plot 42, Jubilee Hills Road No. 36, Near Peddamma Temple, Hyderabad',
                'city': 'Hyderabad',
                'latitude': 17.4326,
                'longitude': 78.4071,
                'google_maps_link': 'https://maps.google.com/?q=17.4326,78.4071',
                'phone_number': '+91 98765 43210',
                'email': 'contact@fitletics.com',
                'opening_time': '05:00',
                'closing_time': '23:00',
                'rating': 4.7,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created gym: {gym.name}'))

        # Create plans
        plans_data = [
            {
                'name': 'Day Pass',
                'duration': 'day',
                'price': 299,
                'features': 'Full gym access, Locker, Towel, Water',
                'is_popular': False,
            },
            {
                'name': 'Weekly Starter',
                'duration': 'week',
                'price': 999,
                'features': 'Full gym access, Locker, Group classes, Fitness assessment',
                'is_popular': False,
            },
            {
                'name': 'Monthly Basic',
                'duration': 'month',
                'price': 2499,
                'features': 'Full gym access, Locker, Group classes, Diet consultation, Access to all equipment',
                'is_popular': True,
            },
            {
                'name': 'Quarterly Premium',
                'duration': 'quarter',
                'price': 5999,
                'features': 'Full gym access, Personal locker, All group classes, 2 PT sessions, Diet plan, Body composition analysis',
                'is_popular': False,
            },
            {
                'name': 'Annual Elite',
                'duration': 'year',
                'price': 19999,
                'features': 'Unlimited gym access, VIP locker, All classes, 12 PT sessions, Custom diet plan, Priority booking, Guest passes (5), Merchandise',
                'is_popular': False,
            },
        ]

        for plan_data in plans_data:
            plan, created = GymPlan.objects.get_or_create(
                gym=gym,
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'  Created plan: {plan.name} - ₹{plan.price}')

        # Create a customer user for testing
        customer_user, created = User.objects.get_or_create(
            username='customer1',
            defaults={
                'email': 'customer@example.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
            }
        )
        if created:
            customer_user.set_password('demo1234')
            customer_user.save()
            from gym_app.models import Customer
            Customer.objects.create(
                user=customer_user,
                phone_number='+91 87654 32109'
            )
            self.stdout.write(self.style.SUCCESS(f'Created customer: customer1'))

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write(self.style.WARNING('\nTest accounts:'))
        self.stdout.write('  Gym Owner: gymowner1 / demo1234')
        self.stdout.write('  Customer:  customer1 / demo1234')
        self.stdout.write(self.style.SUCCESS(f'\nSample gym: {gym.name}'))
