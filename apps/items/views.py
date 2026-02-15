import logging

from django.db.models import Count, QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .filters import ItemFilter
from .models import Item
from .serializers import CategoryDensitySerializer, ItemSerializer

logger = logging.getLogger(__name__)


class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Item CRUD operations.

    list:   GET    /api/items/
    create: POST   /api/items/
    read:   GET    /api/items/{id}/
    update: PUT    /api/items/{id}/
    delete: DELETE /api/items/{id}/ (soft delete)
    """

    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ItemFilter
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name", "price"]
    ordering = ["-created_at"]

    def get_queryset(self) -> QuerySet:
        """Return non-deleted items owned by the authenticated user."""
        return Item.objects.filter(
            is_deleted=False,
            owner=self.request.user,
        ).select_related("owner")

    def perform_create(self, serializer) -> None:
        """Assign the authenticated user as the item owner on creation."""
        serializer.save(owner=self.request.user)
        logger.info(
            "Item created: '%s' by %s",
            serializer.instance.name,
            self.request.user.email,
        )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Soft-delete an item by setting is_deleted=True."""
        instance = self.get_object()
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted", "updated_at"])
        logger.info(
            "Item soft-deleted: id=%s by %s", instance.pk, request.user.email
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="analytics/category-density")
    def category_density(self, request: Request) -> Response:
        """
        Return item count and percentage distribution per category.

        Response: {success, data: {total, categories: [{category, count, percentage}]}}
        """
        queryset = self.get_queryset()
        total = queryset.count()

        if total == 0:
            return Response(
                {"success": True, "data": {"total": 0, "categories": []}}
            )

        categories = (
            queryset
            .values("category")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        result = [
            {
                "category": item["category"],
                "count": item["count"],
                "percentage": round(item["count"] / total * 100, 2),
            }
            for item in categories
        ]

        return Response({
            "success": True,
            "data": {
                "total": total,
                "categories": CategoryDensitySerializer(result, many=True).data,
            },
        })
