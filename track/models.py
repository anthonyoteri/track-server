from datetime import datetime
import time

from django.core.exceptions import ValidationError
from django.db import models

from model_utils.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.SlugField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Project(TimeStampedModel):
    name = models.SlugField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    categories = models.ManyToManyField(Category, related_name="projects")

    def __str__(self):
        return self.name


class Record(TimeStampedModel):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    start_time_epoch = models.PositiveIntegerField()
    stop_time_epoch = models.PositiveIntegerField(blank=True, null=True)

    @property
    def start_time(self):
        return datetime.fromtimestamp(self.start_time_epoch)

    @property
    def stop_time(self):
        if self.stop_time_epoch is None:
            return None
        return datetime.fromtimestamp(self.stop_time_epoch)

    @property
    def elapsed(self):
        if self.stop_time_epoch is None:
            return int(time.time() - self.start_time_epoch)
        return self.stop_time_epoch - self.start_time_epoch

    def clean(self):
        if (
            self.stop_time_epoch is not None
            and self.stop_time_epoch < self.start_time_epoch
        ):
            raise ValidationError("Stop time cannot be before start time")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project.name} [{self.start_time.iso_format()}]"
