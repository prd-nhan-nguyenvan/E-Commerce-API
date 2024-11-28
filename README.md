# E-Commerce API

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
- User Roles (Admin, Staff, User)
    - Admin:

      **Permissions**: Full access to all functionalities, including user management, product management, order
      processing, and reporting.

      **Responsibilities**:
        - Manage users (create, edit, deactivate).
        - Oversee all transactions and orders.
        - Access to sensitive data and configuration settings.
        - Generate reports and analytics regarding user behavior and sales.
    - Staff:

      **Permissions**: Limited access compared to admins; typically can manage products, orders, and assist customers
      but do not have access to user management features.

      **Responsibilities**:
        - Process orders and handle returns/exchanges.
        - Manage inventory and product listings.
        - Provide customer support through queries and issues.
        - Generate reports related to sales performance (if permitted).
    - User:

      **Permissions**: Basic access to view products, make purchases, and manage their own profile.

      **Responsibilities**:
        - Browse the product catalog and view details.
        - Place orders and manage their cart.
        - Leave reviews and ratings for products.
        - Update their personal information and preferences in their profile.

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
core/
├── core/    # Main project folder (settings, URLs)
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
