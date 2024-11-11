from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rides.api.serializers import RideBookingSerializer
from .models import RideBooking
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.cache import cache_page
from taxi.utils.mongo import log_ride
from django.utils import timezone
from taxi.utils.kafka_producer import produce_event


class BookRideUser(generics.CreateAPIView):
    serializer_class = RideBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Log the ride to MongoDB
        log_ride({
            "ride_id": serializer.data.get("id"),
            "rider_id": request.user.id,
            "ride_status": serializer.data.get("ride_status"),
            "timestamp": serializer.data.get("booked_at"),
            "details": serializer.data,
        })

        # Send Kafka event
        produce_event('ride_booked', f'Ride {serializer.data.get("id")} booked by User {request.user.id}')

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RetrieveRideAPI(generics.RetrieveUpdateAPIView):
    serializer_class = RideBookingSerializer
    queryset = RideBooking.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Log the updated ride to MongoDB
        log_ride({
            "ride_id": instance.id,
            "updated_by": request.user.id,
            "ride_status": serializer.data.get("ride_status"),
            "timestamp": serializer.data.get("updated_at"),
            "details": serializer.data,
        })

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
class ListBookedRidesAPI(generics.ListAPIView):
    serializer_class = RideBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = RideBooking.objects.all().order_by("-id")
    filterset_fields = [
        'ride_price', 'payment_method', 'ride_status', 
        'rider__user__first_name', 'rider__user__last_name', 'rider__user__id',
        'driver__user__first_name', 'driver__user__last_name', 'driver__user__id',
    ]

    def get_queryset(self):
        # Adding a custom filter for user-specific bookings if needed
        user = self.request.user
        if user.is_staff:  # Admin can view all bookings
            return RideBooking.objects.all().order_by("-id")
        return RideBooking.objects.filter(rider__user=user).order_by("-id")

class ListBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            rides = RideBooking.objects.filter(rider__user=user).order_by("-booked_at")
            serializer = RideBookingSerializer(rides, many=True)

            # Log the retrieved rides to MongoDB
            log_ride({
                "retrieved_by": user.id,
                "action": "list_rides",
                "timestamp": timezone.now(),
                "ride_count": rides.count(),
            })

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
