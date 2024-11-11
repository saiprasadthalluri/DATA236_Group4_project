from django.db import models
from drivers.models import DriverProfile
from riders.models import RiderProfile
from app_settings.models import SiteSettings
from django.conf import settings

User = settings.AUTH_USER_MODEL

PAYMENT_METHODS = (
    ("Card", "Card"),
    ("Cash", "Cash"),
    ("Wallet", "Wallet"),
)
RIDE_STATUS = (
    ("Pending", "Pending"),
    ("Accepted", "Accepted"),
    ("In Progress", "In Progress"),
    ("Completed", "Completed"),
    ("Canceled", "Canceled"),
)

CAR_TYPE = (
    ("SUV", "SUV"),
    ("Sedan", "Sedan"),
    ("Luxury", "Luxury"),
)

class RideBooking(models.Model):
    agent_created = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rider = models.ForeignKey(RiderProfile, related_name="rider_instance", on_delete=models.DO_NOTHING, null=True)
    driver = models.ForeignKey(DriverProfile, related_name="driver_instance", on_delete=models.SET_NULL, null=True, blank=True)
    pick_up_location = models.CharField(max_length=600)
    pickup_long_lat = models.CharField(max_length=600)
    drop_off_location = models.CharField(max_length=600)
    drop_off_long_lat = models.CharField(max_length=600)
    ride_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    distance = models.CharField(max_length=300, default=0)
    ride_duration = models.CharField(max_length=30, default=0)
    payment_method = models.CharField(max_length=300, choices=PAYMENT_METHODS, default="Cash")
    ride_car_type = models.CharField(max_length=300, choices=CAR_TYPE, default="Sedan")
    ride_status = models.CharField(max_length=300, default="Pending", choices=RIDE_STATUS)
    booked_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def calculate_price(self):
        site_settings = SiteSettings.objects.first()
        if site_settings:
            base_price = site_settings.base_price
            duration_value = float(site_settings.price_minute) * float(self.ride_duration)
            distance_value = float(site_settings.price_km) * float(self.distance)
            self.ride_price = float(base_price) + duration_value + distance_value

    def save(self, *args, **kwargs):
        if not self.pk:  # Only calculate price on creation
            self.calculate_price()
        super(RideBooking, self).save(*args, **kwargs)

    def __str__(self):
        return f"New ride booked {self.ride_status}"
