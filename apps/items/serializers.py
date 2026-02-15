from decimal import Decimal

from rest_framework import serializers

from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for Item CRUD operations."""

    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "description",
            "category",
            "status",
            "price",
            "owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def validate_price(self, value: Decimal) -> Decimal:
        """Ensure price is a positive number."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_name(self, value: str) -> str:
        """Ensure name is not blank after stripping."""
        if not value.strip():
            raise serializers.ValidationError("Name cannot be blank.")
        return value.strip()


class CategoryDensitySerializer(serializers.Serializer):
    """Read-only serializer for category analytics response."""

    category = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()
