from django.contrib import admin
from django.urls import path, include
from api_rest.health_checks import HealthView, LivenessView, ReadinessView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view(), name='health'),
    path('health/live/', LivenessView.as_view(), name='health_live'),
    path('health/ready/', ReadinessView.as_view(), name='health_ready'),
    path('api/', include('api_rest.urls'), name='api_rest_urls'),

]
