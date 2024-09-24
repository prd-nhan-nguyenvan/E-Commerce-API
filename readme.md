# E-COMMERCE API CLONE
This is project to practice Django Rest Framework

## Feature

### 1. **Authentication Module**
   - User Registration
   - Login / Logout
   - Password Reset
   - Token-based authentication (using `SimpleJWT` or `TokenAuthentication`)
   - Social Authentication (optional)

### 2. **Product Management Module**
   - Product Categories
   - Product Listing
   - Product Detail (individual product information)
   - Product Search and Filtering
   - Product Reviews (optional)
   - Inventory Management (optional)

### 3. **User Management Module**
   - User Profiles
   - User Roles (Admin, Customer, etc.)
   - Address Management
   - User Permissions

### 4. **Cart/Order Management Module**
   - Cart System (adding, removing products)
   - Order Placement (creating orders from cart)
   - Order Status Tracking (pending, shipped, delivered)
   - Payment Processing (optional)
   - Order History


## Folder structure
```bash
ecommerce_project/
├── ecommerce_project/    # Main project folder (settings, URLs)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── authentication/       # App for user authentication
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
├── products/             # App for managing products
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
├── users/                # App for managing users
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
├── orders/               # App for managing orders and cart
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
├── static/               # For static files (images, CSS, JS)
├── media/                # For media uploads (product images)
├── manage.py
├── .env                  # Environment variables
└── requirements.txt      # Project dependencies

```
## Apps

1. authentication
2. users
3. products
4. orders

## API

...

## Swagger
