# Case Study API

Django REST Framework ile geliştirilmiş RESTful API. Kullanıcı yönetimi, JWT kimlik doğrulama ve Item CRUD işlemlerini kapsar.

## Teknolojiler

- Python 3.11
- Django 4.2 + Django REST Framework
- PostgreSQL (Docker) / SQLite (local)
- JWT Authentication (simplejwt)
- pytest + factory-boy
- Docker & Docker Compose
- drf-spectacular (OpenAPI/Swagger)

## Kurulum

### Local

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### Docker

```bash
cp .env.example .env
docker-compose up --build
```

Uygulama http://localhost:8000 adresinde çalışır.

## Environment Variables

| Değişken | Açıklama | Varsayılan |
|---|---|---|
| `SECRET_KEY` | Django secret key | insecure-default |
| `DEBUG` | Debug modu | `True` |
| `DATABASE_URL` | Veritabanı bağlantısı | SQLite |

## API Endpoints

### Kullanıcı Yönetimi

| Method | Endpoint | Açıklama | Auth |
|---|---|---|---|
| POST | `/api/users/register/` | Kullanıcı kaydı | Hayır |
| POST | `/api/users/login/` | Kullanıcı girişi (JWT) | Hayır |
| GET | `/api/users/profile/` | Profil bilgisi | Evet |
| PUT | `/api/users/profile/` | Profil güncelleme | Evet |
| POST | `/api/users/token/refresh/` | JWT token yenileme | Hayır |

### Item Yönetimi

| Method | Endpoint | Açıklama | Auth |
|---|---|---|---|
| GET | `/api/items/` | Item listesi (pagination, filter, sort) | Evet |
| POST | `/api/items/` | Yeni item oluştur | Evet |
| GET | `/api/items/{id}/` | Item detay | Evet |
| PUT | `/api/items/{id}/` | Item güncelle | Evet |
| DELETE | `/api/items/{id}/` | Item sil (soft delete) | Evet |
| GET | `/api/items/analytics/category-density/` | Kategori yoğunluk analizi | Evet |

### Dokümantasyon

| Endpoint | Açıklama |
|---|---|
| `/api/schema/` | OpenAPI schema (JSON) |
| `/api/docs/` | Swagger UI |

## Örnek Request/Response

### Register
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "date_joined": "2025-01-01T00:00:00Z"
    },
    "tokens": {
      "access": "eyJ...",
      "refresh": "eyJ..."
    }
  }
}
```

### Login
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```
```json
{
  "success": true,
  "data": {
    "user": {"id": 1, "email": "user@example.com", "first_name": "John", "last_name": "Doe"},
    "tokens": {"access": "eyJ...", "refresh": "eyJ..."}
  }
}
```

### Token Refresh
```bash
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```
```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

### Item Oluştur
```bash
curl -X POST http://localhost:8000/api/items/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "iPhone 15", "category": "electronics", "price": "999.99"}'
```

### Filtreleme & Sıralama
```bash
# Kategori filtresi
GET /api/items/?category=electronics

# Status filtresi
GET /api/items/?status=active

# İsme göre arama
GET /api/items/?name=iphone

# Fiyat aralığı
GET /api/items/?min_price=100&max_price=500

# Sıralama
GET /api/items/?ordering=-price
GET /api/items/?ordering=created_at

# Pagination
GET /api/items/?page=2&per_page=20
```

### Kategori Analizi
```bash
curl http://localhost:8000/api/items/analytics/category-density/ \
  -H "Authorization: Bearer <access_token>"
```
```json
{
  "success": true,
  "data": {
    "total": 3,
    "categories": [
      {"category": "electronics", "count": 2, "percentage": 66.67},
      {"category": "clothing", "count": 1, "percentage": 33.33}
    ]
  }
}
```

### Error Response Format
Tüm hatalar tutarlı formatta döner:
```json
{
  "success": false,
  "error": "BAD_REQUEST",
  "message": "price: Price must be greater than zero.",
  "details": {"price": ["Price must be greater than zero."]}
}
```

## Test

```bash
# Tüm testleri çalıştır
pytest

# Coverage raporu ile
pytest --cov=apps --cov-report=term-missing

# Sadece users testleri
pytest apps/users/tests.py -v

# Sadece items testleri
pytest apps/items/tests.py -v
```

## Proje Yapısı

```
case/
├── config/              # Django proje yapılandırması
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/            # Ortak utilities
│   │   ├── exceptions.py    # Merkezi hata yönetimi
│   │   ├── pagination.py    # Custom pagination
│   │   └── middleware.py     # Request logging
│   ├── users/           # Kullanıcı yönetimi
│   │   ├── models.py        # Custom User model
│   │   ├── serializers.py   # Register, Login, Profile serializers
│   │   ├── views.py         # Auth + Profile views
│   │   └── urls.py
│   └── items/           # Item CRUD + Analytics
│       ├── models.py        # Item model (soft delete)
│       ├── serializers.py   # Item + CategoryDensity serializers
│       ├── filters.py       # django-filter FilterSet
│       ├── views.py         # ModelViewSet + analytics action
│       └── urls.py
├── conftest.py          # pytest fixtures
├── manage.py
├── requirements.txt
├── setup.cfg
├── Dockerfile
├── docker-compose.yml
└── README.md
```
