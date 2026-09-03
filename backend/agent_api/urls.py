from django.urls import path
from . import views

urlpatterns = [
    path('telemetry/ingest/', views.ingest_telemetry),
    path('runs/<uuid:run_id>/trace/', views.get_run_trace),
    path('runs/<uuid:run_id>/gate/', views.resolve_gate),
    path('sensors/', views.get_sensors),
    path('runs/', views.get_runs),
]