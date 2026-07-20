# E-Commerce API

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Marshmallow](https://img.shields.io/badge/Marshmallow-000000?style=for-the-badge)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)

**Author:** Kathy Booth (with contributions from Claude)

A RESTful API built with Flask, Flask-SQLAlchemy, and Flask-Marshmallow that manages Users, Products, and Orders, with a One-to-Many relationship (User → Orders) and a Many-to-Many relationship (Orders ↔ Products). Includes JWT-based authentication, input validation, pagination, and advanced order management.

## Project Structure

```
ecommerce_api/
├── ecommerce_app.py                        # Main application (models, schemas, routes)
├── requirements.txt                        # Python dependencies
├── eCommerce_API.postman_collection.json   # Postman collection for all endpoints
├── .env                                    # Local secrets (never committed to git)
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Create the MySQL Database

Open MySQL Workbench and run:

```sql
CREATE DATABASE ecommerce_api;
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install Flask Flask-SQLAlchemy Flask-Marshmallow marshmallow-sqlalchemy mysql-connector-python python-dotenv flask-jwt-extended
```

### 4. Configure Your Secrets

Create a `.env` file in the project folder (this file is git-ignored and never shared) with:

```
DB_PASSWORD=your_mysql_password_here
JWT_SECRET_KEY=a_long_random_secret_string
```

### 5. Run the App

```bash
python ecommerce_app.py
```

This automatically creates all tables (`user`, `product`, `order`, `order_product`) in your `ecommerce_api` database and starts the server at `http://127.0.0.1:5000`.

## Testing with Postman

1. Open Postman.
2. Click **Import** and select `eCommerce_API.postman_collection.json`.
3. The collection includes a request for every endpoint, including Login.
4. Make sure the app is running locally, then send requests and check responses.
5. For protected endpoints, copy the `access_token` from the Login response and paste it into the request's **Authorization** tab as a **Bearer Token**.

## Authentication

User accounts require a password (hashed with Werkzeug's `generate_password_hash` before storage — plain-text passwords are never saved). Logging in returns a signed JWT access token tied to that user's ID.

**Login**
```json
POST /login
{
  "email": "user@example.com",
  "password": "theirpassword"
}
```

Returns:
```json
{
  "access_token": "eyJhbGciOi..."
}
```

Protected endpoints require this token in the request header as a Bearer Token. Currently protected:

| Endpoint | Protection |
|----------|------------|
| `DELETE /users/<id>` | Requires a valid token, and a user may only delete their own account (`403` if attempting to delete someone else's) |

Deleting a user automatically deletes their orders as well (cascade delete), preventing orphaned records.

## Endpoints

### Users
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| GET | `/users` | Get all users | No |
| GET | `/users/paginated?page=1&per_page=10` | Get paginated users | No |
| GET | `/users/<id>` | Get a user by ID | No |
| POST | `/users` | Create a new user (`name`, `address`, `email`, `password`) | No |
| PUT | `/users/<id>` | Update a user | No |
| DELETE | `/users/<id>` | Delete a user (cascades to their orders) | Yes (own account only) |
| POST | `/login` | Log in and receive a JWT access token | No |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | Get all products |
| GET | `/products/paginated?page=1&per_page=10` | Get paginated products |
| GET | `/products/<id>` | Get a product by ID |
| POST | `/products` | Create a new product |
| PUT | `/products/<id>` | Update a product |
| DELETE | `/products/<id>` | Delete a product |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders` | Get all orders |
| GET | `/orders/<id>` | Get a single order by ID |
| POST | `/orders` | Create a new order (`user_id`, `order_date`) |
| DELETE | `/orders/<id>` | Delete an order |
| GET | `/orders/<id>/total` | Get the total price of all products in an order |
| PUT | `/orders/<order_id>/add_product/<product_id>` | Add a product to an order (no duplicates) |
| DELETE | `/orders/<order_id>/remove_product/<product_id>` | Remove a product from an order |
| GET | `/orders/user/<user_id>` | Get all orders for a user |
| GET | `/orders/<order_id>/products` | Get all products in an order |

## Example Requests

**Create a user**
```json
POST /users
{
  "name": "Ada Lovelace",
  "address": "123 Main St",
  "email": "ada@example.com",
  "password": "securepassword"
}
```

**Log in**
```json
POST /login
{
  "email": "ada@example.com",
  "password": "securepassword"
}
```

**Create an order**
```json
POST /orders
{
  "user_id": 2,
  "order_date": "2026-07-17T10:00:00"
}
```

## Validation

All create/update endpoints validate incoming data using Marshmallow schemas. Invalid or missing data returns a `400 Bad Request` with a clear error message, for example:

```json
{
  "email": ["Not a valid email address."]
}
```

## Notes

- `include_fk = True` is set on `OrderSchema` so `user_id` is recognized and serialized correctly.
- `password_hash` is excluded from `UserSchema` entirely, so it can never be accidentally exposed in an API response.
- The database password and JWT secret key are stored in a local `.env` file (excluded from git) and loaded with `python-dotenv`, so no secrets are committed to the repository.
- Pagination is available on `/users` and `/products` via `?page=` and `?per_page=` query parameters.