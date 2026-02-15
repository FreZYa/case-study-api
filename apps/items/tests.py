import pytest
from django.urls import reverse
from rest_framework import status

from apps.items.models import Item


# ─── Helper ────────────────────────────────────────


@pytest.fixture
def sample_item(user):
    return Item.objects.create(
        name="Test Item",
        description="A test item",
        category="electronics",
        status="active",
        price="29.99",
        owner=user,
    )


@pytest.fixture
def item_payload():
    return {
        "name": "New Item",
        "description": "New description",
        "category": "books",
        "status": "active",
        "price": "19.99",
    }


# ─── CRUD Tests ────────────────────────────────────


@pytest.mark.django_db
class TestItemCreate:
    def test_create_item_success(self, auth_client, item_payload):
        url = reverse("items:item-list")
        response = auth_client.post(url, item_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Item"
        assert response.data["category"] == "books"

    def test_create_item_unauthenticated(self, api_client, item_payload):
        url = reverse("items:item-list")
        response = api_client.post(url, item_payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_item_missing_fields(self, auth_client):
        url = reverse("items:item-list")
        response = auth_client.post(url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_item_negative_price(self, auth_client):
        url = reverse("items:item-list")
        payload = {
            "name": "Bad Item",
            "category": "books",
            "price": "-10.00",
        }
        response = auth_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestItemList:
    def test_list_items(self, auth_client, sample_item):
        url = reverse("items:item-list")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_list_excludes_deleted(self, auth_client, sample_item):
        sample_item.is_deleted = True
        sample_item.save()

        url = reverse("items:item-list")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0


@pytest.mark.django_db
class TestItemDetail:
    def test_get_item_detail(self, auth_client, sample_item):
        url = reverse("items:item-detail", kwargs={"pk": sample_item.pk})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Item"

    def test_get_nonexistent_item(self, auth_client):
        url = reverse("items:item-detail", kwargs={"pk": 9999})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestItemUpdate:
    def test_update_item(self, auth_client, sample_item):
        url = reverse("items:item-detail", kwargs={"pk": sample_item.pk})
        payload = {
            "name": "Updated Item",
            "description": "Updated",
            "category": "electronics",
            "status": "active",
            "price": "49.99",
        }
        response = auth_client.put(url, payload)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Item"
        assert response.data["price"] == "49.99"


@pytest.mark.django_db
class TestItemDelete:
    def test_soft_delete_item(self, auth_client, sample_item):
        url = reverse("items:item-detail", kwargs={"pk": sample_item.pk})
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        sample_item.refresh_from_db()
        assert sample_item.is_deleted is True


# ─── Filter Tests ──────────────────────────────────


@pytest.mark.django_db
class TestItemFilter:
    def test_filter_by_category(self, auth_client, user):
        Item.objects.create(name="Phone", category="electronics", price="999", owner=user)
        Item.objects.create(name="Shirt", category="clothing", price="29", owner=user)

        url = reverse("items:item-list")
        response = auth_client.get(url, {"category": "electronics"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Phone"

    def test_filter_by_status(self, auth_client, user):
        Item.objects.create(name="Active", category="books", status="active", price="10", owner=user)
        Item.objects.create(name="Archived", category="books", status="archived", price="10", owner=user)

        url = reverse("items:item-list")
        response = auth_client.get(url, {"status": "active"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Active"

    def test_search_by_name(self, auth_client, user):
        Item.objects.create(name="iPhone 15", category="electronics", price="999", owner=user)
        Item.objects.create(name="Python Book", category="books", price="29", owner=user)

        url = reverse("items:item-list")
        response = auth_client.get(url, {"name": "iphone"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1


# ─── Analytics Tests ───────────────────────────────


@pytest.mark.django_db
class TestCategoryDensity:
    def test_category_density(self, auth_client, user):
        Item.objects.create(name="Phone", category="electronics", price="999", owner=user)
        Item.objects.create(name="Laptop", category="electronics", price="1999", owner=user)
        Item.objects.create(name="Shirt", category="clothing", price="29", owner=user)

        url = reverse("items:item-category-density")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["total"] == 3

        categories = response.data["data"]["categories"]
        assert len(categories) == 2

        electronics = next(c for c in categories if c["category"] == "electronics")
        assert electronics["count"] == 2
        assert electronics["percentage"] == pytest.approx(66.67, rel=0.01)

    def test_category_density_empty(self, auth_client):
        url = reverse("items:item-category-density")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["total"] == 0
        assert response.data["data"]["categories"] == []
