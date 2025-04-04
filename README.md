# Django Stripe Integration

A Django application that demonstrates integration with Stripe for product management with full CRUD operations.

## Features

- Product management (Create, Read, Update, Delete)
- Shopping cart functionality
- Stripe Checkout integration for secure payments
- Transaction history with downloadable receipts
- Automatic product syncing with Stripe
- Environment-based configuration
- Responsive UI

## Prerequisites

- Python 3.8+
- Django 5.0+
- Stripe account with API keys

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd stripe-integration-django
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
DEBUG=True
SECRET_KEY=your-django-secret-key
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
STRIPE_PUBLIC_KEY=your-stripe-publishable-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

5. Replace the placeholder values in `.env` with your actual configuration:
   - Generate a Django secret key
   - Add your Stripe API keys (available in your Stripe dashboard)

6. Run migrations:
```bash
python manage.py migrate
```

7. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

## Running the Application

1. Start the development server:
```bash
python manage.py runserver
```

2. Access the application at `http://localhost:8000`

## Project Structure

```
stripe-integration-django/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── stripe_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── products/
    ├── __init__.py
    ├── admin.py
    ├── models.py
    ├── views.py
    ├── forms.py
    └── templates/
        └── products/
            ├── base.html
            ├── product_list.html
            ├── product_form.html
            ├── product_confirm_delete.html
            ├── cart.html
            ├── checkout_success.html
            └── transaction_list.html
```

## Deployment

1. Update `.env` for production:
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECRET_KEY=your-secure-secret-key
```

2. Configure your production database in `DATABASE_URL`

3. Collect static files:
```bash
python manage.py collectstatic
```

4. Set up a production web server (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn stripe_project.wsgi:application
```

5. Configure Nginx or Apache as a reverse proxy

## Security Considerations

- Never commit `.env` file to version control
- Keep your Stripe API keys secure
- Use HTTPS in production
- Regularly update dependencies
- Follow Django's deployment checklist

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
