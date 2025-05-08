# Backend Coderr API

This repository contains the backend for the Coderr project. It is a Django REST Framework (DRF) application structured for modularity, maintainability, and best practices.

## Features
- Modular Django project with separate apps for authentication, profiles, offers, orders, reviews, and infos
- RESTful API endpoints for all resources
- JWT/Token-based authentication
- Permissions and role-based access control
- Admin interface enabled
- Filtering, pagination, and ordering for list endpoints
- Automated tests for all critical functionality

## Project Structure
- `core/`: Main project folder (settings, urls, wsgi, asgi)
- `auth_app/`, `profiles_app/`, `offers_app/`, `orders_app/`, `reviews_app/`, `infos_app/`: Each app has its own `api/` folder with `serializers.py`, `views.py`, `urls.py`, `permissions.py`, etc.
- `mediafiles/`: Uploaded files (e.g., profile images)
- `requirements.txt`: All dependencies

## Setup & Installation
1. **Clone the repository**
2. **Create and activate a virtual environment**
   ```bash
   python -m venv env
   env\Scripts\activate  # On Windows
   # source env/bin/activate  # On Linux/Mac
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Documentation
- Swagger UI: `/swagger/`
- Redoc: `/redoc/`

## Main API Endpoints

| Resource     | Method | Endpoint                                       | Description                              |
| ------------ | ------ | ---------------------------------------------- | ---------------------------------------- |
| Auth         | POST   | /api/registration/                             | Register a new user                      |
| Auth         | POST   | /api/login/                                    | Login and receive token                  |
| Profiles     | GET    | /api/profiles/customer/                        | List all customer profiles               |
| Profiles     | GET    | /api/profiles/business/                        | List all business profiles               |
| Profiles     | GET    | /api/profile/<pk>/                             | Retrieve or update a user profile        |
| Offers       | GET    | /api/offers/                                   | List all offers                          |
| Offers       | POST   | /api/offers/                                   | Create a new offer (business only)       |
| Offers       | GET    | /api/offers/<pk>/                              | Retrieve, update, or delete an offer     |
| OfferDetails | GET    | /api/offerdetails/                             | List all offer details                   |
| OfferDetails | GET    | /api/offerdetails/<id>/                        | Retrieve a specific offer detail         |
| Orders       | GET    | /api/orders/                                   | List all orders for the user             |
| Orders       | POST   | /api/orders/                                   | Create a new order (customer only)       |
| Orders       | PATCH  | /api/orders/<pk>/                              | Update order status (business only)      |
| Orders       | DELETE | /api/orders/<pk>/                              | Delete order (staff only)                |
| Orders       | GET    | /api/order-count/<business_user_id>/           | Get order count for a business           |
| Orders       | GET    | /api/completed-order-count/<business_user_id>/ | Get completed order count for a business |
| Reviews      | GET    | /api/reviews/                                  | List all reviews                         |
| Reviews      | POST   | /api/reviews/                                  | Create a new review (customer only)      |
| Reviews      | PATCH  | /api/reviews/<pk>/                             | Update a review (owner only)             |
| Reviews      | DELETE | /api/reviews/<pk>/                             | Delete a review (owner only)             |
| Infos        | GET    | /api/base-info/                                | Get general statistics/info              |
| Admin        | GET    | /admin/                                        | Django admin interface                   |

All endpoints are resource-oriented and follow REST conventions. For details on parameters and responses, see Swagger UI (`/swagger/`) or Redoc (`/redoc/`).

## Testing
- Run all tests:
  ```bash
  python manage.py test
  ```
- Test coverage is >95% for all critical endpoints.

## Important Notes
- **Do not commit or upload the `db.sqlite3` or any database files to GitHub.**
- The backend is separated from any frontend code and should be in its own repository.
- All environment-specific settings (e.g., secrets) should be managed via environment variables or `.env` files (not included).

## Special Considerations
- Each app uses a clear naming convention (e.g., `auth_app`, `offers_app`).
- All API endpoints are resource-oriented and follow REST best practices.
- The admin interface is available at `/admin/`.
- For any custom management commands, see the `management/commands/` folders in each app.

## Contact
For questions or support, contact the maintainer at mail@jan-holtschke.de
