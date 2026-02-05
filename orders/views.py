from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name="ADMIN").exists():
            return Order.objects.all().prefetch_related("items")

        return Order.objects.filter(user=user).prefetch_related("items")


    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer
