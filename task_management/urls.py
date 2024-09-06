"""
URL configuration for task_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Configuration for Swagger API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Task Management API",  # Title for the API docs
        default_version="v1",  # API version
        description="API documentation for the Task Management application",  # Brief description of the API
        contact=openapi.Contact(
            email="marko.zrinjanin.uw@gmail.com"
        ),  # Contact information
        license=openapi.License(name="BSD License"),  # License information
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # Make API docs publicly accessible
)

# URL configuration for the project
urlpatterns = [
    path(
        "", RedirectView.as_view(url="/redoc/", permanent=False), name="index"
    ),  # Redirect from root url to ReDoc UI
    path("admin/", admin.site.urls),  # Admin interface
    path("api/v1/", include("tasks.urls")),  # Include API URLs from the `tasks` app
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),  # Swagger UI
    path(
        "redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),  # ReDoc UI
]
