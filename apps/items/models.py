from django.db import models


class Item(models.Model):
    """Product item with category, status and soft-delete support."""

    CATEGORY_CHOICES = [
        ("electronics", "Electronics"),
        ("clothing", "Clothing"),
        ("food", "Food"),
        ("books", "Books"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("archived", "Archived"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="active")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="items"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category"], name="idx_item_category"),
            models.Index(fields=["status"], name="idx_item_status"),
            models.Index(fields=["owner", "is_deleted"], name="idx_item_owner_active"),
            models.Index(fields=["created_at"], name="idx_item_created"),
        ]

    def __str__(self) -> str:
        return self.name
