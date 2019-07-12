import logging

from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import serializers, status, viewsets

from track.models import Category, Project, Record

from track.selectors import get_active_record, get_entries_per_week

from track.services import (
    add_project_to_category,
    create_category,
    create_project,
    create_record,
    update_record,
)


log = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    class CategorySerializer(serializers.ModelSerializer):
        projects = serializers.SlugRelatedField(
            slug_field="name", read_only=True, many=True
        )
        description = serializers.CharField(required=False)

        class Meta:
            model = Category
            fields = ("name", "projects", "description")

        def create(self, validated_data):
            validated_data.pop("projects", None)

            return create_category(**validated_data)

    queryset = Category.objects.all().order_by("created")
    serializer_class = CategorySerializer
    lookup_field = "name"


class ProjectViewSet(viewsets.ModelViewSet):
    class ProjectSerializer(serializers.ModelSerializer):
        categories = serializers.SlugRelatedField(
            slug_field="name", queryset=Category.objects.all(), many=True
        )

        class Meta:
            model = Project
            fields = ("categories", "name", "description")

        @transaction.atomic
        def create(self, validated_data):
            categories = validated_data.pop("categories", None)
            project = create_project(**validated_data)

            for category in categories:
                add_project_to_category(project=project, category=category)

            return project

    queryset = Project.objects.all().order_by("created")
    serializer_class = ProjectSerializer
    lookup_field = "name"


class RecordViewSet(viewsets.ModelViewSet):
    class RecordSerializer(serializers.ModelSerializer):
        project = serializers.SlugRelatedField(
            slug_field="name", queryset=Project.objects.all()
        )
        start_time = serializers.DateTimeField()
        stop_time = serializers.DateTimeField(required=False)

        class Meta:
            model = Record
            fields = ("project", "start_time", "stop_time", "elapsed")

        @transaction.atomic
        def create(self, validated_data):
            if "stop_time" not in validated_data:
                validated_data["stop_time"] = None

            record = create_record(**validated_data)
            return record

        @transaction.atomic
        def update(self, instance, validated_data):

            record = update_record(
                record=instance,
                project=validated_data["project"],
                start_time=validated_data["start_time"],
                stop_time=validated_data.get("stop_time"),
            )
            return record

    queryset = Record.objects.all().order_by("-start_time_epoch")
    serializer_class = RecordSerializer


class ActiveRecordView(GenericAPIView):
    class OutputSerializer(serializers.ModelSerializer):
        project = serializers.SlugRelatedField(
            slug_field="name", read_only=True
        )

        class Meta:
            model = Record
            fields = ("id", "project", "start_time", "stop_time", "elapsed")

    class InputSerializer(serializers.Serializer):
        project = serializers.SlugRelatedField(
            slug_field="name", queryset=Project.objects.all()
        )
        stop_time = serializers.DateTimeField()

    def get(self, request: Request) -> Response:

        active = get_active_record()
        if active is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        content = self.OutputSerializer(active).data
        return Response(content, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request: Request) -> Response:
        active = get_active_record()
        if active is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if active.project != serializer.validated_data["project"]:
            log.warning(
                "project from request %s does not match active project %s",
                serializer.validated_data["project"],
                active.project,
            )
            return Response(status=status.HTTP_403_FORBIDDEN)

        record = update_record(
            record=active,
            project=active.project,
            start_time=active.start_time,
            stop_time=serializer.validated_data["stop_time"],
        )

        return Response(
            self.OutputSerializer(record).data, status=status.HTTP_200_OK
        )


class ReportWeekView(GenericAPIView):
    class OutputSerializer(serializers.Serializer):
        class DaySerializer(serializers.Serializer):
            date = serializers.DateField(read_only=True)
            records = serializers.DictField(
                child=serializers.IntegerField(read_only=True), read_only=True
            )
            total = serializers.IntegerField(read_only=True)

        week_number = serializers.CharField(read_only=True)
        projects = serializers.ListField(read_only=True)
        days = DaySerializer(many=True, read_only=True)

    def get(self, request: Request, year: int, week_number: int) -> Response:
        iso_week_number = f"{year}-W{int(week_number):02}"
        log.info("Get report for week %s", iso_week_number)

        data = get_entries_per_week(week_number=iso_week_number)
        content = self.OutputSerializer(data).data

        return Response(content, status=status.HTTP_200_OK)


class ReportCategoryWeekView(GenericAPIView):
    class OutputSerializer(serializers.Serializer):
        class DaySerializer(serializers.Serializer):
            date = serializers.DateField(read_only=True)
            records = serializers.DictField(
                child=serializers.IntegerField(read_only=True), read_only=True
            )
            total = serializers.IntegerField(read_only=True)

        week_number = serializers.CharField(read_only=True)
        category = serializers.CharField(read_only=True)
        projects = serializers.ListField(read_only=True)
        days = DaySerializer(many=True, read_only=True)

    def get(
        self, request: Request, category: str, year: int, week_number: int
    ) -> Response:
        iso_week_number = f"{year}-W{week_number}"

        data = get_entries_per_week(
            week_number=iso_week_number, category=category
        )
        content = self.OutputSerializer(data).data

        return Response(content, status=status.HTTP_200_OK)
