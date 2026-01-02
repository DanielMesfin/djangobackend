# broker/api/v1/urls/__init__.py
from django.urls import path, include
from .auth import urlpatterns as auth_urls
from .user import urlpatterns as user_urls

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('', include((user_urls, 'broker_api'), namespace='broker_api')),
]