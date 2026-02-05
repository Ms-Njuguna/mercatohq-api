from rest_framework import viewsets
from .models import Inventory
from .serializers import InventorySerializer
from config.permissions import IsAdmin


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related("product")
    serializer_class = InventorySerializer
    permission_classes = [IsAdmin]
