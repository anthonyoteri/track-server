from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
import pytest

from track.services import (
    add_project_to_category,
    create_category,
    create_project,
    create_record,
    remove_project_from_category,
    update_record,
)
from . import factories


@pytest.mark.django_db
def test_create_category():
    category_stub = factories.CategoryFactory.stub()

    data = {
        "name": category_stub.name,
        "description": category_stub.description,
    }
    category = create_category(**data)

    assert category.name == category_stub.name
    assert category.description == category_stub.description


@pytest.mark.django_db
def test_create_category_without_description():
    category_stub = factories.CategoryFactory.stub()

    data = {"name": category_stub.name, "description": None}
    category = create_category(**data)

    assert category.name == category_stub.name
    assert category.description is None


@pytest.mark.django_db
def test_create_project():
    project_stub = factories.ProjectFactory.stub()

    data = {"name": project_stub.name, "description": project_stub.description}
    project = create_project(**data)

    assert project.name == project_stub.name
    assert project.description == project_stub.description


@pytest.mark.django_db
def test_create_project_without_description():
    project_stub = factories.ProjectFactory.stub()

    data = {"name": project_stub.name, "description": None}
    project = create_project(**data)

    assert project.name == project_stub.name
    assert project.description is None


@pytest.mark.django_db
def test_add_project_to_category():

    project = factories.ProjectFactory()
    category = factories.CategoryFactory()

    add_project_to_category(project=project, category=category)

    assert project in category.projects.all()


@pytest.mark.django_db
def test_remove_project_from_category():

    project1 = factories.ProjectFactory()
    project2 = factories.ProjectFactory()
    category = factories.CategoryFactory()

    category.projects.add(project1)
    category.projects.add(project2)

    remove_project_from_category(project=project2, category=category)

    assert project2 not in category.projects.all()


@pytest.mark.django_db
def test_create_record():

    project = factories.ProjectFactory()
    record_stub = factories.RecordFactory.stub()

    record = create_record(
        project=project,
        start_time=datetime.fromtimestamp(record_stub.start_time_epoch),
        stop_time=datetime.fromtimestamp(record_stub.stop_time_epoch),
    )

    assert record.project == project
    assert record.start_time_epoch == record_stub.start_time_epoch
    assert record.stop_time_epoch == record_stub.stop_time_epoch


@pytest.mark.django_db
def test_create_record_no_stop_time():

    project = factories.ProjectFactory()
    record_stub = factories.RecordFactory.stub()

    record = create_record(
        project=project,
        start_time=datetime.fromtimestamp(record_stub.start_time_epoch),
        stop_time=None,
    )

    assert record.project == project
    assert record.start_time_epoch == record_stub.start_time_epoch
    assert record.stop_time_epoch is None


@pytest.mark.django_db
def test_create_record_stop_time_in_the_past():

    project = factories.ProjectFactory()
    record_stub = factories.RecordFactory.stub()

    with pytest.raises(ValidationError):
        create_record(
            project=project,
            start_time=datetime.fromtimestamp(record_stub.start_time_epoch),
            stop_time=datetime.fromtimestamp(record_stub.start_time_epoch - 1),
        )


@pytest.mark.django_db
def test_update_record_project():

    project = factories.ProjectFactory()
    record = factories.RecordFactory(project=project)

    new_project = factories.ProjectFactory()

    result = update_record(
        record=record,
        project=new_project,
        start_time=record.start_time,
        stop_time=record.stop_time,
    )

    assert result.project == new_project


@pytest.mark.django_db
def test_update_record_start_time():

    record = factories.RecordFactory()

    new_start_time = record.start_time - timedelta(hours=1)

    result = update_record(
        record=record,
        project=record.project,
        start_time=new_start_time,
        stop_time=record.stop_time,
    )

    assert result.start_time_epoch == datetime.timestamp(new_start_time)


@pytest.mark.django_db
def test_update_record_stop_time():

    record = factories.RecordFactory()
    new_stop_time = record.stop_time + timedelta(hours=1)

    result = update_record(
        record=record,
        project=record.project,
        start_time=record.start_time,
        stop_time=new_stop_time,
    )

    assert result.stop_time_epoch == datetime.timestamp(new_stop_time)


@pytest.mark.django_db
def test_update_record_remove_stop_time():

    record = factories.RecordFactory()
    result = update_record(
        record=record,
        project=record.project,
        start_time=record.start_time,
        stop_time=None,
    )

    assert result.stop_time_epoch is None
