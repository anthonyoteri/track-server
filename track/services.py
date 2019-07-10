from datetime import datetime
from typing import Optional

import logging

from .models import Category, Project, Record

log = logging.getLogger(__name__)


def create_category(
    *, name: str, description: Optional[str] = None
) -> Category:
    """Create a new category."""
    log.info("create category %s with description: '%s'", name, description)
    category = Category(name=name, description=description)
    category.full_clean()
    category.save()

    return category


def create_project(*, name: str, description: Optional[str] = None) -> Project:
    """Create a new project."""
    log.info("create project %s with description: '%s'", name, description)

    project = Project(name=name, description=description)
    project.full_clean()
    project.save()

    return project


def create_record(
    *, project: Project, start_time: datetime, stop_time: Optional[datetime]
) -> Record:
    """Create a new record."""
    log.info(
        "create new record on project %s with start_time %s",
        project,
        start_time,
    )

    start_time_epoch: Optional[float] = datetime.timestamp(start_time)

    stop_time_epoch: Optional[float] = None
    if stop_time is not None:
        stop_time_epoch = datetime.timestamp(stop_time)

    record = Record(
        project=project,
        start_time_epoch=start_time_epoch,
        stop_time_epoch=stop_time_epoch,
    )

    record.full_clean()
    record.save()

    return record


def update_record(
    *,
    record: Record,
    project: Project,
    start_time: datetime,
    stop_time: Optional[datetime]
) -> Record:
    """Update one or more fields on an existing record."""
    log.info(
        "record %s will be updated with project %s to start %s and stop %s",
        record.id,
        project,
        start_time,
        stop_time,
    )

    start_time_epoch = datetime.timestamp(start_time)

    stop_time_epoch: Optional[float] = None
    if stop_time is not None:
        stop_time_epoch = datetime.timestamp(stop_time)

    record.project = project
    record.start_time_epoch = start_time_epoch
    record.stop_time_epoch = stop_time_epoch

    record.full_clean()
    record.save()

    return record


def add_project_to_category(*, project: Project, category: Category) -> None:
    """Adds the given project to a category."""
    category.projects.add(project)


def remove_project_from_category(
    *, project: Project, category: Category
) -> None:
    """Removes the given project from a category."""
    category.projects.remove(project)
