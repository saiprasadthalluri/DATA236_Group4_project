from rest_framework import serializers
from rides.models import RideBooking
from drivers.models import DriverProfile
from riders.models import RiderProfile

class RideBookingSerializer(serializers.ModelSerializer):
    rider_id = serializers.IntegerField(write_only=True, required=True)
    driver_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = RideBooking
        fields = [
            "id", "pick_up_location", "drop_off_location", "pickup_long_lat", "drop_off_long_lat", "ride_car_type",
            "rider_id", "driver_id", "rider", "driver", "ride_price", "distance", "ride_duration",
            "payment_method", "ride_status", "booked_at", "modified_at", "agent_created"
        ]
        depth = 1

    def create(self, validated_data):
        rider_id = validated_data.pop('rider_id', None)
        if not validated_data["pick_up_location"] or not validated_data["drop_off_location"]:
            raise serializers.ValidationError({"Error": "Pick up and drop off locations are required."})
        if not rider_id:
            raise serializers.ValidationError({"Error": "Rider field is required."})

        if RideBooking.objects.filter(rider_id=rider_id, ride_status="Pending").exists():
            raise serializers.ValidationError({"Error": "You cannot book more than one ride at the same time."})

        rider_profile = RiderProfile.objects.filter(id=rider_id).first()
        if not rider_profile:
            raise serializers.ValidationError({"Error": "Invalid rider."})

        validated_data['rider'] = rider_profile
        ride = RideBooking.objects.create(**validated_data)
        return ride

    def update(self, instance, validated_data):
        if instance.ride_status in ["Canceled", "Completed"]:
            raise serializers.ValidationError({"Error": "Ride is no longer available for updates."})

        driver_id = validated_data.pop("driver_id", None)
        if driver_id and validated_data.get("ride_status") == "Accepted":
            if RideBooking.objects.filter(driver_id=driver_id, ride_status="Accepted").exists():
                raise serializers.ValidationError({"Error": "Finish the previous ride before accepting a new one."})
            driver_profile = DriverProfile.objects.filter(id=driver_id).first()
            if not driver_profile:
                raise serializers.ValidationError({"Error": "Invalid driver."})
            instance.driver = driver_profile

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
