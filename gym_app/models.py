from django.db import models
from django.contrib.auth.models import User

class Member(models.Model):
    SUBSCRIPTION_CHOICES = (
        ('Basic', 'Basic - Gym Access Only'),
        ('Premium', 'Premium - Gym + Classes'),
        ('Elite', 'Elite - Gym + Classes + Personal Trainer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='Basic')
    subscription_status = models.BooleanField(default=True) # True = Active, False = Expired
    join_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type}"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Card', 'Credit/Debit Card'),
        ('UPI', 'UPI/Online'),
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='Cash')
    remarks = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.member.user.username} - {self.amount}"
