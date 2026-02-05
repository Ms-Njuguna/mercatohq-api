from rest_framework import serializers
from .models import Product
from inventory.models import Inventory

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ["quantity"]

class ProductSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "description",
            "price",
            "is_active",
            "inventory",
            "created_at",
        ]

class ProductCreateSerializer(serializers.ModelSerializer):
    stock = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "description",
            "price",
            "is_active",
            "stock",
        ]

    def create(self, validated_data):
        stock = validated_data.pop("stock")
        product = Product.objects.create(**validated_data)
        Inventory.objects.create(product=product, quantity=stock)
        return product
