from django.conf.urls import url
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

router = routers.DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"records", RecordViewSet)

urlpatterns = [
    url(regex="^records/active/$", view=ActiveRecordView.as_view()),
    url(
        regex="^reports/week/(?P<year>[0-9]{4})/(?P<week_number>[0-9]{1,2})/$",
        view=ReportWeekView.as_view(),
    ),
    url(
        regex="^reports/week/(?P<year>[0-9]{4})/(?P<week_number>[0-9]{1,2})/(?P<category>[-\w]+)/$",  # noqa E501
        view=ReportCategoryWeekView.as_view(),
    ),
    path("", include(router.urls)),
]
