from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from inventory.models import Inventory


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

            order.total_price = total
            order.save()

        return order
