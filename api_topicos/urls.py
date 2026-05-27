from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django_prometheus.urls')),
    path('health/', include('health_check.urls')),
    path('api/', include('api_rest.urls'), name='api_rest_urls'),

]
