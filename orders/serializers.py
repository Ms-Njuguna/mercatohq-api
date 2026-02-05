from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from inventory.models import Inventory


# ---------- READ SERIALIZERS ----------

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "quantity", "price")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "status",
            "total",
            "items",
            "created_at",
        )


# ---------- WRITE SERIALIZERS ----------

class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("product", "quantity")


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ("items",)

    def create(self, validated_data):
        request = self.context["request"]
        items_data = validated_data.pop("items")

        with transaction.atomic():
            order = Order.objects.create(user=request.user)
            total = 0

            for item in items_data:
                product = item["product"]
                quantity = item["quantity"]

                inventory = Inventory.objects.select_for_update().get(
                    product=product
                )

                if inventory.quantity < quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock for {product.name}"
                    )

                inventory.quantity -= quantity
                inventory.save()

                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )

                total += order_item.price * quantity

            order.total = total
            order.save()

        return order
