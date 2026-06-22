"""URL configuration for the core project.

Routes the admin site and includes the per-app API URL modules. Both apps
expose their routes under the shared `/api/` prefix.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),
    path('api/', include('kanban_app.api.urls')),
]
