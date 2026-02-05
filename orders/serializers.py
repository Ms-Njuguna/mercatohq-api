from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from inventory.models import Inventory


class OrderItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ["product_id", "quantity"]

    def validate(self, data):
        try:
            inventory = Inventory.objects.get(product_id=data["product_id"])
        except Inventory.DoesNotExist:
            raise serializers.ValidationError("Product inventory not found")

        if data["quantity"] > inventory.quantity:
            raise serializers.ValidationError(
                f"Not enough stock. Available: {inventory.quantity}"
            )

        return data


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "items"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        with transaction.atomic():
            order = Order.objects.create(user=user)

            total = 0

            for item in items_data:
                inventory = Inventory.objects.select_for_update().get(
                    product_id=item["product_id"]
                )

                inventory.quantity -= item["quantity"]
                inventory.save()

                price = inventory.product.price * item["quantity"]

                OrderItem.objects.create(
                    order=order,
                    product=inventory.product,
                    quantity=item["quantity"],
                    price=price,
                )

                total += price

            order.total = total
            order.save()

        return order


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total", "items", "created_at"]
