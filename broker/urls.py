# broker/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

urlpatterns = [
    path('api/v1/', include('broker.api.v1.urls')),

]