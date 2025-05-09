# Coderr Backend

Coderr Backend is a modular Django REST Framework (DRF) backend for a service marketplace platform. It is designed for maintainability, scalability, and clean code, providing a robust API for user management, offers, orders, reviews, and platform statistics.

## Features
- **Modular project structure:** Each domain (auth, profiles, offers, orders, reviews, infos) is implemented as a separate Django app for clear separation of concerns.
- **RESTful API:** Resource-oriented endpoints for all major entities, following REST best practices.
- **Authentication & Authorization:** Token-based authentication (DRF Token Auth) and role-based permissions (customer, business, staff).
- **Filtering, ordering, and pagination:** Flexible list endpoints with support for filtering, ordering, and pagination.
- **Admin interface:** Django admin enabled for easy data management.
- **Automated testing:** Comprehensive test coverage for all critical functionality.
- **OpenAPI documentation:** Interactive API docs available via Swagger UI and Redoc.

## Project Structure
- `core/` – Main project configuration (settings, urls, wsgi, asgi)
- `auth_app/` – User registration, login, and authentication
- `profiles_app/` – User profile management (customer & business)
- `offers_app/` – Offer and offer detail management
- `orders_app/` – Order management
- `reviews_app/` – Review and rating system
- `infos_app/` – Platform statistics/info endpoints
- `mediafiles/` – Uploaded files (e.g., profile images)
- `requirements.txt` – Python dependencies

## Getting Started
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
5. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Overview
- All endpoints are prefixed with `/api/`
- Interactive API docs: `/swagger/` (Swagger UI), `/redoc/` (Redoc)
- See below for a full list of main API endpoints.

## Environment & Configuration
- **Database:** Default is SQLite for development. For production, configure your preferred database in `.env.production` using only the `DATABASE_URL` variable (recommended with django-environ).
- **Media files:** Uploaded files are stored in the `mediafiles/` directory.
- **Environment variables:**
  - Create a `.env.development` (for local development) and a `.env.production` (for deployment).
  - Each file should contain its own, secret `SECRET_KEY` and all required settings:
    - `SECRET_KEY` (required, unique per environment)
    - `DEBUG` (True/False)
    - `ALLOWED_HOSTS` (comma-separated list)
    - `DATABASE_URL` (full DB URL, e.g. for SQLite or Postgres)
    - `FORCE_SCRIPT_NAME` (optional, only in production, for deployments under a URL prefix)
    - **STATIC_URL:** In development `/static/`, in production `/be-coderr/static/` (see .env.production)
    - **MEDIA_URL:** In development `/media/`, in production `/be-coderr/media/`
    - `CORS_ALLOWED_ORIGINS` (comma-separated list, e.g. for dev: localhost:5500,127.0.0.1:5500; for prod: https://backend.jan-holtschke.de)
    - (add more as needed for your project, e.g. email, storage, etc.)
  - Example `.env.development`:
    ```env
    SECRET_KEY=dev-secret-key-please-change
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    DATABASE_URL=sqlite:///db.sqlite3
    # FORCE_SCRIPT_NAME=/be-coderr  # Uncomment if you want to test with a URL prefix in development
    # STATIC_URL and MEDIA_URL are not set for development (default: /static/ and /media/)
    CORS_ALLOWED_ORIGINS=localhost:5500,127.0.0.1:5500
    ```
  - Example `.env.production`:
    ```env
    SECRET_KEY=prod-very-secret-key
    DEBUG=False
    ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
    DATABASE_URL=postgres://yourdbuser:yourdbpassword@yourdbhost:5432/yourdbname
    FORCE_SCRIPT_NAME=/be-coderr
    STATIC_URL=/be-coderr/static/
    MEDIA_URL=/be-coderr/media/
    CORS_ALLOWED_ORIGINS=https://backend.jan-holtschke.de
    ```
  - These files are **not** checked into version control (see `.gitignore`).
  - For production deployments, you can specify which file to load via the `DJANGO_ENV_FILE` environment variable.
- **Admin:** The Django admin interface is available at `/admin/` (or under your prefix, e.g. `/be-coderr/admin/` if `FORCE_SCRIPT_NAME` is set).

## Deployment

To deploy this Django project to production, follow these steps:

1. **Prepare your environment**
   - Use a secure server (e.g. Ubuntu, Debian, etc.)
   - Install Python 3.10+ and pip
   - Set up a virtual environment and activate it

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Create a `.env.production` file (see example above) with a unique, secret `SECRET_KEY`, `DEBUG=False`, your production `ALLOWED_HOSTS`, and your production database settings.
   - Set the environment variable `DJANGO_ENV_FILE` to the path of your `.env.production` file, e.g.:
     ```bash
     export DJANGO_ENV_FILE=/path/to/your/.env.production
     ```

4. **Apply migrations and collect static files**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

5. **Create a superuser (if needed)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the application**
   - For production, use a WSGI server like Gunicorn:
     ```bash
     gunicorn core.wsgi:application --bind 0.0.0.0:8000
     ```
   - Use a reverse proxy (e.g. nginx) to serve static files and forward requests to Gunicorn.

7. **Security notes**
   - Never set `DEBUG=True` in production.
   - Keep your `.env.production` file and `SECRET_KEY` secret and out of version control.
   - Use HTTPS in production.

For more details, see the [Django deployment checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/).

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
Run all tests with:
```bash
python manage.py test
```

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.

## Contact
For questions or support, contact the maintainer at mail@jan-holtschke.de
