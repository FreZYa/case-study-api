from django_filters import rest_framework as filters

from .models import Item


class ItemFilter(filters.FilterSet):
    """Filter items by name (partial), category, status, and price range."""

    name = filters.CharFilter(lookup_expr="icontains")
    category = filters.ChoiceFilter(choices=Item.CATEGORY_CHOICES)
    status = filters.ChoiceFilter(choices=Item.STATUS_CHOICES)
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Item
        fields = ["name", "category", "status", "min_price", "max_price"]
