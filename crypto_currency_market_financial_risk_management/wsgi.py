"""
WSGI config for crypto_currency_market_financial_risk_management

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_currency_market_financial_risk_management.settings')
application = get_wsgi_application()
