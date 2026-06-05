from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from api_rest.health_checks import HealthView, LivenessView, ReadinessView
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(
    title="API Topicos Avancados",
    description="Documentacao OpenAPI da API REST do projeto.",
    version="1.0.0",
    renderer_classes=[JSONOpenAPIRenderer],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthView.as_view(), name='health'),
    path('health/live/', LivenessView.as_view(), name='health_live'),
    path('health/ready/', ReadinessView.as_view(), name='health_ready'),
    path('openapi/', schema_view, name='openapi-schema'),
    path('swagger/', TemplateView.as_view(template_name='swagger-ui.html'), name='swagger-ui'),
    path('api/', include('api_rest.urls'), name='api_rest_urls'),

]
