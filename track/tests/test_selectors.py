from datetime import datetime, date, timedelta

import pytest

from track.selectors import (
    get_active_record,
    get_elapsed_time,
    get_elapsed_time_per_category,
    get_entries_per_day,
    get_entries_per_week,
)

from . import factories


@pytest.mark.django_db
def test_get_active_record_all_stopped():
    factories.RecordFactory.create_batch(10)
    active = get_active_record()
    assert active is None


@pytest.mark.django_db
def test_get_active_record_one_is_running():
    factories.RecordFactory.create_batch(9)
    target = factories.RecordFactory(stop_time_epoch=None)

    active = get_active_record()
    assert active is not None
    assert active == target
    assert active.stop_time_epoch is None


@pytest.mark.django_db
def test_get_elapsed_time():

    project1 = factories.ProjectFactory()
    project2 = factories.ProjectFactory()

    now = datetime.now().replace(microsecond=0)
    for offset in range(24, 0, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project1,
        )

    assert get_elapsed_time(project=project1) == 24 * 60 * 60
    assert get_elapsed_time(project=project2) == 0


@pytest.mark.django_db
def test_get_elapsed_time_with_lower_bounds():

    project1 = factories.ProjectFactory()

    now = datetime.now().replace(microsecond=0)

    for offset in range(24, 0, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project1,
        )

    assert (
        get_elapsed_time(project=project1, begin=now - timedelta(hours=6))
        == 6 * 60 * 60
    )


@pytest.mark.django_db
def test_get_elapsed_time_with_upper_bounds():

    project1 = factories.ProjectFactory()

    now = datetime.now().replace(microsecond=0)

    for offset in range(24, 0, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project1,
        )

    assert (
        get_elapsed_time(project=project1, end=now - timedelta(hours=6))
        == 18 * 60 * 60
    )


@pytest.mark.django_db
def test_get_elapsed_time_with_lower_and_upper_bounds():

    project1 = factories.ProjectFactory()

    now = datetime.now().replace(microsecond=0)

    for offset in range(24, 0, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project1,
        )

    assert (
        get_elapsed_time(
            project=project1,
            begin=now - timedelta(hours=8),
            end=now - timedelta(hours=6),
        )
        == 2 * 60 * 60
    )


@pytest.mark.django_db
def test_get_elapsed_time_per_category():

    category1 = factories.CategoryFactory()
    category2 = factories.CategoryFactory()
    category3 = factories.CategoryFactory()

    project1 = factories.ProjectFactory()
    project2 = factories.ProjectFactory()

    project1.categories.add(category1)
    project1.categories.add(category2)

    project2.categories.add(category1)

    now = datetime.now().replace(microsecond=0)
    for offset in range(48, 24, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project1,
        )

    for offset in range(24, 0, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project2,
        )

    assert get_elapsed_time_per_category(category=category1) == 48 * 60 * 60
    assert get_elapsed_time_per_category(category=category2) == 24 * 60 * 60
    assert get_elapsed_time_per_category(category=category3) == 0


@pytest.mark.django_db
def test_get_elapsed_time_per_category_with_lower_bounds():

    category1 = factories.CategoryFactory()
    category2 = factories.CategoryFactory()

    project1 = factories.ProjectFactory()
    project2 = factories.ProjectFactory()

    project1.categories.add(category1)
    project1.categories.add(category2)

    project2.categories.add(category1)

    now = datetime.now().replace(microsecond=0)
    for offset in range(48, 24, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project1,
        )

    for offset in range(24, 0, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project2,
        )

    assert (
        get_elapsed_time_per_category(
            category=category1, begin=now - timedelta(hours=6)
        )
        == 6 * 60 * 60
    )
    assert (
        get_elapsed_time_per_category(
            category=category2, begin=now - timedelta(hours=6)
        )
        == 0
    )


@pytest.mark.django_db
def test_get_elapsed_time_per_category_with_upper_bounds():

    category1 = factories.CategoryFactory()
    category2 = factories.CategoryFactory()

    project1 = factories.ProjectFactory()
    project2 = factories.ProjectFactory()

    project1.categories.add(category1)
    project1.categories.add(category2)

    project2.categories.add(category1)

    now = datetime.now().replace(microsecond=0)
    for offset in range(48, 24, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project1,
        )

    for offset in range(24, 0, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project2,
        )

    assert (
        get_elapsed_time_per_category(
            category=category1, end=now - timedelta(hours=6)
        )
        == 42 * 60 * 60
    )
    assert (
        get_elapsed_time_per_category(
            category=category2, end=now - timedelta(hours=6)
        )
        == 24 * 60 * 60
    )


@pytest.mark.django_db
def test_get_entries_per_day():
    project1 = factories.ProjectFactory()

    now = datetime.now().replace(microsecond=0)
    for offset in range(48, 0, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project1,
        )

    expected = {
        project1: int(
            (
                now.replace(minute=0, second=0)
                - now.replace(hour=0, minute=0, second=0)
            ).total_seconds()
        )
    }

    assert get_entries_per_day(day=now.date()) == expected


@pytest.mark.django_db
def test_get_entries_per_day_for_category():

    category = factories.CategoryFactory()
    project1 = factories.ProjectFactory()
    project2 = factories.ProjectFactory()

    category.projects.add(project1)

    now = datetime.now().replace(microsecond=0)
    for offset in range(48, 0, -1):
        start_time = now - timedelta(hours=offset)
        stop_time = start_time + timedelta(hours=1)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project1,
        )

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(
                start_time + timedelta(minutes=5)
            ),
            stop_time_epoch=datetime.timestamp(
                stop_time - timedelta(minutes=5)
            ),
            project=project2,
        )

    expected = {
        project1: int(
            (
                now.replace(minute=0, second=0)
                - now.replace(hour=0, minute=0, second=0)
            ).total_seconds()
        )
    }

    assert (
        get_entries_per_day(day=now.date(), category=category.name) == expected
    )


@pytest.mark.parametrize("with_category", [False, True])
@pytest.mark.django_db
def test_get_entries_per_week(with_category):

    category = factories.CategoryFactory()
    project1 = factories.ProjectFactory()

    category.projects.add(project1)

    now = datetime(2019, 7, 9)  # A Tuesday
    for offset in range(24 * 14, 0, -1):
        start_time = now - timedelta(hours=offset) + timedelta(minutes=15)
        stop_time = start_time + timedelta(minutes=30)

        factories.RecordFactory(
            start_time_epoch=datetime.timestamp(start_time),
            stop_time_epoch=datetime.timestamp(stop_time),
            project=project1,
        )

    expected = {
        "week_number": "2019-W27",
        "projects": [project1.name],
        "days": [
            {
                "date": date(2019, 7, n),
                "records": {project1.name: 24 * 30 * 60},
                "total": 24 * 30 * 60,
            }
            for n in range(1, 8)
        ],
    }

    category_param = None
    if with_category:
        expected["category"] = category.name
        category_param = category.name

    assert (
        get_entries_per_week(week_number="2019-W27", category=category_param)
        == expected
    )
