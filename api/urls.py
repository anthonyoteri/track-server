from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    ProjectViewSet,
    RecordViewSet,
    ActiveRecordView,
    ReportCategoryWeekView,
    ReportWeekView,
)

app_name = "api"

router = routers.DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"records", RecordViewSet)

urlpatterns = [
    path("records/active/", ActiveRecordView.as_view(), name="record-active"),
    path(
        "reports/week/<int:year>/<int:week_number>/",
        ReportWeekView.as_view(),
        name="report-week",
    ),
    path(
        "reports/week/<int:year>/<int:week_number>/<slug:category>/",
        ReportCategoryWeekView.as_view(),
        name="report-week-category",
    ),
    path("", include(router.urls)),
]
