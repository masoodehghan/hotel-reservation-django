from rest_framework import generics, permissions
from .serializers import (
    HotelSerializer,  GallerySerializer, RoomReadSerializer,
    RoomWriteSerializer, ReservationSerializer
)
from ...models import Hotel, Room, Gallery, Reservation
from .permissions import IsHostOrReadOnly, IsGalleryHost, IsRoomHostOrReadOnly


class HotelListCreatedView(generics.ListCreateAPIView):
    serializer_class = HotelSerializer

    def get_queryset(self):
        queryset = Hotel.objects.select_related('location').order_by('-id')
        return queryset

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


class HotelGalleryView(generics.CreateAPIView):
    serializer_class = GallerySerializer
    permission_classes = [IsGalleryHost]
    queryset = Gallery.objects.all()

    def perform_create(self, serializer):
        serializer.save(hotel_pk=self.kwargs['hotel_pk'])


class HotelDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HotelSerializer
    permission_classes = [IsHostOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        return Hotel.objects.prefetch_related('gallery').all()


class RoomListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsRoomHostOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoomWriteSerializer
        else:
            return RoomReadSerializer

    def get_queryset(self):
        queryset = Room.objects.select_related('hotel', 'hotel__location',
                                               'hotel__host')

        return queryset.order_by('-id')


class RoomListByHotelView(generics.ListAPIView):
    serializer_class = RoomReadSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Room.objects.select_related('hotel', 'hotel__location')

        return queryset.filter(hotel__slug=self.kwargs['hotel_slug'])


class RoomGalleryView(generics.CreateAPIView):
    serializer_class = GallerySerializer
    permission_classes = [IsGalleryHost]
    queryset = Gallery.objects.all()

    def perform_create(self, serializer):
        serializer.save(room_pk=self.kwargs['room_pk'])


class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsRoomHostOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RoomWriteSerializer
        else:
            return RoomReadSerializer

    lookup_field = 'uuid'

    def get_queryset(self):
        queryset = Room.objects.select_related('hotel__host', 'hotel__location')

        return queryset


class ReservationCreate(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)

    def get_queryset(self):
        return Reservation.objects.filter(guest_id=self.request.user.id)