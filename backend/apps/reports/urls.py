from django.urls import path
from .api.views import ReportGenerateView

app_name = 'reports'

urlpatterns = [
    path('generate/', ReportGenerateView.as_view(), name='report-generate'),
]